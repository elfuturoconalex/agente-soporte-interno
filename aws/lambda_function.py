"""
Agente de Soporte Interno (versión AWS) - Fase 2.

Es el mismo agente de preguntar.py, pero en la nube:
1) Busca los 5 pedazos más parecidos en la Knowledge Base de Bedrock (Retrieve).
2) Si ninguno se parece lo suficiente (UMBRAL), responde "no lo sé" SIN llamar a Claude.
3) Si sí hay pedazos, se los pasa a Claude Haiku 4.5 con MIS reglas.
4) Anota la traza (tiempo, tokens, costo, fuentes) en CloudWatch.

Variables de entorno (se configuran en la consola de Lambda, no en el código):
  KB_ID   -> el ID de la Knowledge Base
  UMBRAL  -> puntaje mínimo para llamar a Claude (ej. 0.38)
  MODELO  -> (opcional) el modelo de Claude; si no está, usa Haiku 4.5
"""
import json
import os
import time

import boto3

KB_ID = os.environ["KB_ID"]
UMBRAL = float(os.environ.get("UMBRAL", "0.38"))
MODELO = os.environ.get("MODELO", "global.anthropic.claude-haiku-4-5-20251001-v1:0")
MAX_LARGO_PREGUNTA = 500

kb = boto3.client("bedrock-agent-runtime")   # para buscar en la Knowledge Base
claude = boto3.client("bedrock-runtime")     # para hablar con Claude

INSTRUCCIONES = """Eres el asistente de soporte interno de Nimbo Soluciones.
Respondes preguntas de los empleados usando ÚNICAMENTE los fragmentos de documentos que te doy.

Reglas:
1. Usa solo la información de los fragmentos. No uses conocimiento propio ni supongas nada.
2. Después de cada dato, cita su fuente entre corchetes con el nombre del documento, así: [viaticos-y-gastos].
3. Si los fragmentos responden la pregunta, aunque sea en parte, responde con lo que sí dicen y aclara qué falta.
   Puedes razonar con los datos (por ejemplo, 3 semanas = 15 días hábiles).
4. Solo si los fragmentos no tienen NADA relacionado con la pregunta, responde exactamente:
   "No lo sé: no encontré esa información en los documentos de Nimbo." y sugiere a qué área contactar si los fragmentos lo indican.
5. Responde en español, de forma breve y clara (máximo 5 renglones).
6. Escribe en texto plano: sin negritas, sin asteriscos y sin títulos."""

NO_LO_SE = "No lo sé: no encontré esa información en los documentos de Nimbo."


def responder(codigo, datos):
    """Arma la respuesta en el formato que entiende API Gateway (y la consola)."""
    return {
        "statusCode": codigo,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(datos, ensure_ascii=False),
    }


def leer_pregunta(event):
    """La pregunta puede llegar directo (prueba en consola) o dentro de 'body' (API Gateway)."""
    if "body" in event and event["body"]:
        try:
            event = json.loads(event["body"])
        except (TypeError, json.JSONDecodeError):
            return None
    pregunta = str(event.get("pregunta", "")).strip()
    return pregunta or None


def nombre_documento(resultado):
    """De 's3://bucket/documentos/viaticos-y-gastos.md' saca 'viaticos-y-gastos'."""
    uri = resultado.get("location", {}).get("s3Location", {}).get("uri", "desconocido")
    return uri.split("/")[-1].rsplit(".", 1)[0]


def lambda_handler(event, context):
    inicio = time.time()
    pregunta = leer_pregunta(event)

    if not pregunta:
        return responder(400, {"error": "Falta la pregunta. Ejemplo: {\"pregunta\": \"¿Puedo hacer home office?\"}"})
    if len(pregunta) > MAX_LARGO_PREGUNTA:
        return responder(400, {"error": f"La pregunta es muy larga (máximo {MAX_LARGO_PREGUNTA} caracteres)."})

    traza = {"pregunta": pregunta, "proveedor": "bedrock", "modelo": MODELO, "umbral": UMBRAL}

    # 1) Buscar los 5 pedazos más parecidos en la Knowledge Base
    t0 = time.time()
    busqueda = kb.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": pregunta},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )
    resultados = busqueda["retrievalResults"]
    traza["segundos_busqueda"] = round(time.time() - t0, 2)
    traza["pedazos"] = [
        {"documento": nombre_documento(r), "puntaje": round(r.get("score", 0), 3)} for r in resultados
    ]
    mejor = max((r.get("score", 0) for r in resultados), default=0)
    traza["mejor_puntaje"] = round(mejor, 3)

    # 2) Freno: si nada se parece lo suficiente, no le preguntamos a Claude
    if mejor < UMBRAL:
        traza.update({"llamo_a_claude": False, "costo_usd": 0, "segundos_total": round(time.time() - inicio, 2)})
        print("TRAZA " + json.dumps(traza, ensure_ascii=False))
        return responder(200, {"respuesta": NO_LO_SE, "fuentes": [], "costo_usd": 0, "mejor_puntaje": traza["mejor_puntaje"]})

    # 3) Armar los fragmentos con su fuente y pedirle la respuesta a Claude
    fragmentos = "\n\n".join(
        f"<fragmento documento=\"{nombre_documento(r)}\">\n{r['content']['text']}\n</fragmento>"
        for r in resultados
    )
    t0 = time.time()
    salida = claude.converse(
        modelId=MODELO,
        system=[{"text": INSTRUCCIONES}],
        messages=[{"role": "user", "content": [{"text": f"Fragmentos:\n\n{fragmentos}\n\nPregunta: {pregunta}"}]}],
        inferenceConfig={"maxTokens": 500, "temperature": 0},
    )
    texto = salida["output"]["message"]["content"][0]["text"].replace("**", "")   # sin negritas, aunque Claude las ponga
    tokens_in = salida["usage"]["inputTokens"]
    tokens_out = salida["usage"]["outputTokens"]
    costo = tokens_in * 1 / 1_000_000 + tokens_out * 5 / 1_000_000   # Haiku 4.5: $1 entrada / $5 salida por millón

    fuentes = sorted({nombre_documento(r) for r in resultados if f"[{nombre_documento(r)}]" in texto})

    # 4) Anotar la traza en CloudWatch
    traza.update({
        "llamo_a_claude": True,
        "segundos_claude": round(time.time() - t0, 2),
        "tokens_entrada": tokens_in,
        "tokens_salida": tokens_out,
        "costo_usd": round(costo, 6),
        "fuentes_citadas": fuentes,
        "segundos_total": round(time.time() - inicio, 2),
    })
    print("TRAZA " + json.dumps(traza, ensure_ascii=False))

    return responder(200, {"respuesta": texto, "fuentes": fuentes, "costo_usd": round(costo, 6), "mejor_puntaje": traza["mejor_puntaje"]})
