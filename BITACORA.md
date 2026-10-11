# Bitácora · Agente de Soporte Interno (RAG)

Diario de aprendizaje del agente #2, por sesión de trabajo (cada sesión es de 1 a 2 horas y puede abarcar varios días). En cada una: qué hice, qué aprendí, problemas y siguiente paso.

---

## Sesión 1: Empezar por el final (arquitectura, repo y documentos)
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

---

## Sesión 2: El agente funciona en mi Mac (Fase 1)
*9 al 11 de octubre de 2026*

### Qué hice
- **Paso A2 (chunking):** `cortar.py` convirtió los 7 documentos en **48 pedazos**, cada uno con su documento, título y sección.
- Creé el entorno virtual (`.venv`) e instalé `fastembed`, `numpy`, `anthropic` y `python-dotenv`.
- **Pasos A3 y A4:** `vectorizar.py` convirtió cada pedazo en un vector de **384 números** con un modelo gratuito que corre en mi Mac (`paraphrase-multilingual-MiniLM-L12-v2`) y los guardó en `vector_store/`.
- **Pasos 3 y 4:** `buscar.py` encuentra los 5 pedazos más parecidos a una pregunta.
- **Paso 5:** `preguntar.py` le pasa la pregunta y los 5 pedazos a Claude con reglas: responder solo con esa información, citar la fuente y decir "no lo sé" si no está.

### Resultados
| Pregunta | Resultado |
|---|---|
| ¿Cuántos días de vacaciones tengo con 2 años? | ✅ 14 días + fuente (el pedazo correcto llegó en 3er lugar y Claude lo eligió) |
| ¿Cuánto me dan para comida en un viaje nacional? | ✅ $900 MXN por día + fuente ("comida" encontró "Alimentos") |
| ¿Cuál es la capital de Francia? | ✅ "No lo sé", sin llamar a Claude (puntaje 0.15 < umbral 0.30) |
| ¿Puedo hacer home office? | ⚠️ La búsqueda no trajo el pedazo del modelo híbrido |

Costo por pregunta: **~$0.0013 USD**.

### Qué aprendí
- **Por qué se corta:** para encontrar el párrafo exacto, mandarle solo eso a Claude (menos tokens) y poder citar la fuente.
- **Búsqueda por significado:** cada texto se convierte en "coordenadas"; "comida" y "alimentos" quedan cerca. Cmd + F no lo encontraría.
- **La búsqueda no es perfecta:** por eso se traen 5 pedazos y Claude elige el que de verdad responde.
- **El umbral del "no lo sé":** si ningún pedazo se parece lo suficiente, no se llama a Claude. Ahorra dinero y evita inventos.
- **Medir la búsqueda y la respuesta por separado:** primero "¿trajo el pedazo correcto?", luego "¿Claude respondió bien?". Como en redes: primero ping, luego la aplicación.

### Problemas y cómo los resolví
- **`ImportError: cannot import name 'buscar'`** → tenía `buscar.py` abierto en VS Code con la versión vieja y se guardó encima de la nueva. Gana el último que guarda. Solución: cerrar la pestaña sin guardar cuando el archivo se actualiza.
- **Mostré mi llave de Claude en una captura del `.env`** → borré la llave en la consola de Anthropic, creé una nueva y la puse en los dos proyectos. Regla: nunca tomar captura de un `.env`.
- **"Home office" no encontró el pedazo correcto** → lo guardo como pregunta del examen de la Fase 3 para medir mejoras.

### Siguiente
- Cerrar la Fase 1 y preparar el ADR de la Fase 2: ¿qué vector store usar en AWS?
