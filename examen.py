"""
Examen del agente (Fase 3): manda las 20 preguntas a la API y califica cada respuesta.

Uso:
  export AGENTE_API_URL="https://<MI-API>.execute-api.us-east-1.amazonaws.com/preguntar"
  python examen.py

Califica así:
  - Preguntas con respuesta: aprueba si cita el documento correcto Y menciona los datos clave.
  - Preguntas sin respuesta: aprueba si dice "No lo sé".
Guarda el detalle en salidas/examen_resultados.csv
"""
import csv
import json
import os
import time
import unicodedata
import urllib.request

URL = os.environ.get("AGENTE_API_URL")
if not URL:
    raise SystemExit('Falta la URL. Escribe primero: export AGENTE_API_URL="https://<MI-API>.execute-api.us-east-1.amazonaws.com/preguntar"')


def normal(texto):
    """Minúsculas y sin acentos, para comparar sin fallar por un tilde."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def preguntar(pregunta):
    datos = json.dumps({"pregunta": pregunta}).encode("utf-8")
    req = urllib.request.Request(URL, data=datos, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def calificar(p, r):
    respuesta = r.get("respuesta", "")
    dijo_no_se = normal(respuesta).startswith("no lo se")
    if p["documento"] is None:
        return dijo_no_se, "" if dijo_no_se else "debía decir 'no lo sé'"
    if dijo_no_se:
        return False, "dijo 'no lo sé' y sí había respuesta"
    validos = p["documento"] if isinstance(p["documento"], list) else [p["documento"]]
    if not any(d in r.get("fuentes", []) for d in validos):
        return False, f"no citó {' ni '.join(validos)}"
    faltan = [c for c in p["claves"] if normal(c) not in normal(respuesta)]
    if faltan:
        return False, f"faltan datos: {', '.join(faltan)}"
    return True, ""


preguntas = json.load(open("examen_preguntas.json", encoding="utf-8"))
filas, aprobadas, costo_total = [], 0, 0.0

for p in preguntas:
    try:
        r = preguntar(p["pregunta"])
    except Exception as e:
        r = {"respuesta": f"ERROR: {e}", "fuentes": []}
    ok, motivo = calificar(p, r)
    aprobadas += ok
    costo_total += r.get("costo_usd", 0) or 0
    puntaje = r.get("mejor_puntaje", "")
    tipo = "con respuesta" if p["documento"] else "sin respuesta"
    print(f"{'✅' if ok else '❌'} {p['id']:>2}. [{puntaje}] ({tipo}) {p['pregunta']}" + (f"  → {motivo}" if motivo else ""))
    filas.append({
        "id": p["id"], "pregunta": p["pregunta"], "tipo": tipo, "aprobada": ok, "motivo": motivo,
        "mejor_puntaje": puntaje, "fuentes": " ".join(r.get("fuentes", [])),
        "costo_usd": r.get("costo_usd", ""), "respuesta": r.get("respuesta", ""), "esperado": p["esperado"],
    })
    time.sleep(1)   # respetamos el límite de la API (2 por segundo)

os.makedirs("salidas", exist_ok=True)
with open("salidas/examen_resultados.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=filas[0].keys())
    w.writeheader()
    w.writerows(filas)

print(f"\n📊 Calificación: {aprobadas}/{len(preguntas)}  ·  Costo total: ${costo_total:.4f} USD")

# Para calibrar el umbral: puntajes de cada grupo
con = sorted(f["mejor_puntaje"] for f in filas if f["tipo"] == "con respuesta" and f["mejor_puntaje"] != "")
sin = sorted(f["mejor_puntaje"] for f in filas if f["tipo"] == "sin respuesta" and f["mejor_puntaje"] != "")
if con and sin:
    print(f"🎯 Puntajes con respuesta: del {con[0]} al {con[-1]}")
    print(f"🎯 Puntajes sin respuesta: del {sin[0]} al {sin[-1]}")
    print("   El umbral ideal queda entre el más alto de 'sin respuesta' y el más bajo de 'con respuesta'.")
