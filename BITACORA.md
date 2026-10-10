# Bitácora · Agente de Soporte Interno (RAG)

Diario de aprendizaje del agente #2. Cada día: qué hice, qué aprendí, problemas y siguiente paso.

---

## Día 1: Empezar por el final (arquitectura, repo y documentos)
*8 de octubre de 2026*

### Qué hice
- Definí el agente #2: un chat de soporte interno que responde con los documentos de la empresa, **cita sus fuentes** y dice **"no lo sé"** si no encuentra la respuesta.
- Empecé por el final: un **diagrama de arquitectura preliminar** para usarlo como mapa durante todo el proyecto.
- Configuré **Google Drive para escritorio** con mi cuenta personal para sincronizar solo la carpeta `docs/`.
- Creé el repositorio `agente-soporte-interno`, **público desde el primer commit**, con un `.gitignore` completo (incluye `vector_store/` y archivos de Terraform).
- Creé los documentos de una **empresa ficticia (Nimbo Soluciones)**: vacaciones, trabajo remoto, viáticos, FAQ de TI, seguridad, onboarding y código de conducta.

### Qué aprendí
- **RAG (Retrieval-Augmented Generation):** antes de responder, el agente **busca** en los documentos y Claude responde **solo** con lo que encontró. Así no inventa.
- **Dos flujos:**
  - **Ingesta (A1–A4):** preparar la "biblioteca": subir documentos, cortarlos en pedazos, convertirlos en vectores y guardarlos.
  - **Consulta (1–7):** cada pregunta: buscar los pedazos más parecidos, pedirle a Claude la respuesta con fuentes y devolverla.
- **Vector store:** una biblioteca ordenada **por significado**, no por orden alfabético. "Vacaciones" queda cerca de "días libres".
- **Sin "ticket":** responder una pregunta tarda segundos, así que la API contesta directo (a diferencia del Agente Investigador).
- **Documentos con datos concretos** (días, montos, plazos) para poder comprobar después si el agente responde exacto o inventa.
- **Separar trabajo y personal:** los archivos del proyecto van en mi Drive personal, no en el del trabajo.

### Problemas y cómo los resolví
- **La conexión de Drive de Claude estaba en mi cuenta del trabajo** → instalé Google Drive para escritorio con mi cuenta personal y sincronizo solo `docs/`.
- **GitHub Desktop quería crear el repo en `Documents/GitHub`** → usé "Add Existing Repository" y elegí mi carpeta `proyectos/agente-soporte-interno`.
- **Arrastré sin querer una captura a la Terminal** → cerré la Terminal sin dar Enter; no pasó nada.

### Siguiente
- Leer los documentos de Nimbo.
- Fase 1: preparar el entorno de Python (`.venv`, librerías y `.env`).
