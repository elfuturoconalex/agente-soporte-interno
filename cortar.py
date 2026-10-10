"""
Paso A2 del diagrama: cortar los documentos en pedazos (chunking).

Lee cada documento de la carpeta documentos/, lo corta por secciones (##)
y guarda todos los pedazos en salidas/pedazos.json, cada uno con su fuente.
"""
import json
from pathlib import Path

CARPETA_DOCUMENTOS = Path("documentos")
ARCHIVO_SALIDA = Path("salidas/pedazos.json")
MAX_CARACTERES = 1200   # Si una sección es más larga, se corta en partes


def cortar_documento(ruta):
    """Corta un documento en pedazos: uno por cada sección que empieza con ##."""
    texto = ruta.read_text(encoding="utf-8")
    lineas = texto.splitlines()

    # El título del documento es la primera línea que empieza con "# "
    titulo = next((l[2:].strip() for l in lineas if l.startswith("# ")), ruta.stem)

    pedazos = []
    seccion = "Introducción"
    contenido = []

    def guardar():
        cuerpo = "\n".join(contenido).strip()
        if not cuerpo:
            return
        # Si la sección es muy larga, se corta por párrafos
        partes, actual = [], ""
        for parrafo in cuerpo.split("\n\n"):
            if actual and len(actual) + len(parrafo) > MAX_CARACTERES:
                partes.append(actual)
                actual = ""
            actual = f"{actual}\n\n{parrafo}" if actual else parrafo
        partes.append(actual)

        for parte in partes:
            pedazos.append({
                "id": f"{ruta.stem}-{len(pedazos) + 1}",
                "documento": ruta.name,
                "titulo": titulo,
                "seccion": seccion,
                # Cada pedazo lleva su título y sección: así no pierde el contexto
                "texto": f"{titulo} > {seccion}\n\n{parte}",
            })

    for linea in lineas:
        if linea.startswith("## "):
            guardar()
            seccion = linea[3:].strip()
            contenido = []
        elif not linea.startswith("# "):
            contenido.append(linea)
    guardar()
    return pedazos


def main():
    todos = []
    for ruta in sorted(CARPETA_DOCUMENTOS.glob("*.md")):
        pedazos = cortar_documento(ruta)
        print(f"📄 {ruta.name}: {len(pedazos)} pedazos")
        todos.extend(pedazos)

    ARCHIVO_SALIDA.parent.mkdir(exist_ok=True)
    ARCHIVO_SALIDA.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")

    promedio = sum(len(p["texto"]) for p in todos) // len(todos)
    print(f"\n✂️  Total: {len(todos)} pedazos · {promedio} caracteres en promedio")
    print(f"💾 Guardados en {ARCHIVO_SALIDA}")
    print("\nEjemplo de un pedazo:\n" + "-" * 40)
    print(todos[1]["texto"])


if __name__ == "__main__":
    main()
