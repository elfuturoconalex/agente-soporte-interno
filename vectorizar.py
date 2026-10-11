"""
Pasos A3 y A4 del diagrama: convertir los pedazos en vectores y guardarlos.

A3: cada pedazo se convierte en un vector (sus "coordenadas de significado")
    con un modelo de embeddings gratuito que corre en tu Mac.
A4: los vectores se guardan en el vector store local (carpeta vector_store/).

Antes de correr este programa, corre cortar.py.
"""
import json
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

ARCHIVO_PEDAZOS = Path("salidas/pedazos.json")
CARPETA_VECTOR_STORE = Path("vector_store")
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Entiende español


def main():
    pedazos = json.loads(ARCHIVO_PEDAZOS.read_text(encoding="utf-8"))
    print(f"📚 {len(pedazos)} pedazos para convertir en vectores")

    # A3: el modelo convierte cada texto en una lista de números (un vector)
    print(f"🧠 Cargando el modelo {MODELO} (la primera vez se descarga, ~220 MB)...")
    modelo = TextEmbedding(MODELO)
    vectores = np.array(list(modelo.embed([p["texto"] for p in pedazos])))
    print(f"🔢 Listo: {vectores.shape[0]} vectores de {vectores.shape[1]} números cada uno")

    # A4: guardar los vectores y, junto a ellos, el texto y la fuente de cada pedazo
    CARPETA_VECTOR_STORE.mkdir(exist_ok=True)
    np.save(CARPETA_VECTOR_STORE / "vectores.npy", vectores)
    (CARPETA_VECTOR_STORE / "pedazos.json").write_text(
        json.dumps(pedazos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"💾 Vector store guardado en {CARPETA_VECTOR_STORE}/")

    print("\nAsí se ven las \"coordenadas\" del primer pedazo (solo los primeros 8 números):")
    print(np.round(vectores[0][:8], 3))


if __name__ == "__main__":
    main()
