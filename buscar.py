"""
Pasos 3 y 4 del diagrama: buscar los pedazos más parecidos a una pregunta.

Convierte la pregunta en un vector con el MISMO modelo y busca los pedazos
cuyos vectores están más cerca (búsqueda por significado, no por palabras).

Uso:  python buscar.py "¿cuánto me dan para comida en un viaje?"
"""
import json
import sys
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

CARPETA_VECTOR_STORE = Path("vector_store")
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP = 5   # Cuántos pedazos traer

_modelo = None


def similitud(pregunta_vector, vectores):
    """Qué tan cerca está la pregunta de cada pedazo: 1 = idéntico, 0 = nada que ver."""
    pregunta_vector = pregunta_vector / np.linalg.norm(pregunta_vector)
    vectores = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    return vectores @ pregunta_vector


def buscar(pregunta, top=TOP):
    """Regresa una lista de (puntaje, pedazo) con los pedazos más parecidos."""
    global _modelo
    if _modelo is None:
        _modelo = TextEmbedding(MODELO)

    vectores = np.load(CARPETA_VECTOR_STORE / "vectores.npy")
    pedazos = json.loads((CARPETA_VECTOR_STORE / "pedazos.json").read_text(encoding="utf-8"))

    pregunta_vector = next(iter(_modelo.embed([pregunta])))
    puntajes = similitud(pregunta_vector, vectores)
    mejores = np.argsort(puntajes)[::-1][:top]
    return [(float(puntajes[i]), pedazos[i]) for i in mejores]


def main():
    pregunta = " ".join(sys.argv[1:]) or "¿Cuánto me dan para comida en un viaje nacional?"
    print(f"\n❓ Pregunta: {pregunta}\n")
    print(f"🔍 Los {TOP} pedazos más parecidos:\n")
    for lugar, (puntaje, p) in enumerate(buscar(pregunta), start=1):
        print(f"{lugar}. [{puntaje:.2f}] {p['id']}  ·  {p['titulo']} > {p['seccion']}")


if __name__ == "__main__":
    main()
