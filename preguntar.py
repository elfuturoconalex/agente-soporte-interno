"""
El agente de soporte completo (versión local): pasos 3, 4, 5 y 6 del diagrama.

1) Busca los 5 pedazos más parecidos a la pregunta (buscar.py).
2) Si ninguno se parece lo suficiente, responde "no lo sé" SIN llamar a Claude.
3) Si sí hay pedazos relevantes, se los pasa a Claude con reglas estrictas:
   responder solo con esa información y citar la fuente.

Uso:  python preguntar.py "¿Cuántos días de vacaciones tengo con 2 años?"
"""
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

from buscar import buscar

load_dotenv()                       # Lee ANTHROPIC_API_KEY del archivo .env
claude = Anthropic()

MODELO = "claude-haiku-4-5"
UMBRAL = 0.30   # Si el mejor pedazo tiene menos que esto, no hay información útil

INSTRUCCIONES = """Eres el asistente de soporte interno de Nimbo Soluciones.
Respondes preguntas de los empleados usando ÚNICAMENTE los fragmentos de documentos que te doy.

Reglas:
1. Usa solo la información de los fragmentos. No uses conocimiento propio ni supongas nada.
2. Después de cada dato, cita su fuente entre corchetes, así: [Política de vacaciones > 1. Días de vacaciones por antigüedad].
3. Si los fragmentos no contienen la respuesta, responde exactamente:
   "No lo sé: no encontré esa información en los documentos de Nimbo." y sugiere a qué área contactar si los fragmentos lo indican.
4. Responde en español, de forma breve y clara (máximo 5 renglones)."""

NO_LO_SE = "No lo sé: no encontré esa información en los documentos de Nimbo."


def preguntar(pregunta):
    resultados = buscar(pregunta)
    mejor_puntaje = resultados[0][0]

    print(f"\n❓ {pregunta}")
    print(f"🔍 Mejor coincidencia: {mejor_puntaje:.2f} ({resultados[0][1]['id']})")

    # Freno 1: si nada se parece a la pregunta, ni siquiera le preguntamos a Claude
    if mejor_puntaje < UMBRAL:
        print(f"🚫 Ningún pedazo pasa el umbral de {UMBRAL}: no se llama a Claude.\n")
        print(f"🤖 {NO_LO_SE}\n")
        return

    # Armamos los fragmentos que verá Claude, cada uno con su fuente
    fragmentos = "\n\n".join(
        f"<fragmento fuente=\"{p['titulo']} > {p['seccion']}\" documento=\"{p['documento']}\">\n{p['texto']}\n</fragmento>"
        for _, p in resultados
    )

    respuesta = claude.messages.create(
        model=MODELO,
        max_tokens=500,
        system=INSTRUCCIONES,
        messages=[{"role": "user", "content": f"Fragmentos:\n\n{fragmentos}\n\nPregunta: {pregunta}"}],
    )
    texto = respuesta.content[0].text
    entrada, salida = respuesta.usage.input_tokens, respuesta.usage.output_tokens
    costo = entrada * 1 / 1_000_000 + salida * 5 / 1_000_000

    print(f"\n🤖 {texto}\n")
    print("📚 Pedazos que se le dieron a Claude:")
    for puntaje, p in resultados:
        print(f"   [{puntaje:.2f}] {p['documento']} > {p['seccion']}")
    print(f"\n💰 Tokens: {entrada} entrada, {salida} salida · Costo: ${costo:.5f} USD\n")


if __name__ == "__main__":
    preguntar(" ".join(sys.argv[1:]) or "¿Cuántos días de vacaciones tengo si llevo 2 años?")
