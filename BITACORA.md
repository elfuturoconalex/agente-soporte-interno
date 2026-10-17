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

---

## Sesión 3: Mi base de conocimiento en AWS (Fase 2)
*12 de octubre de 2026*

### Qué hice
- Escribí el **ADR 001**: elegí **S3 Vectors** como vector store (barato, sin servidor). Pierdo la búsqueda híbrida; la compenso después con una segunda búsqueda de Claude.
- Creé un bucket de S3 y subí los 7 documentos de Nimbo a la carpeta `documentos/`.
- Creé una **Bedrock Knowledge Base** (tipo clásico con vector store) con **Titan Text Embeddings V2** y **S3 Vectors**.
- Hice el **Sync**: AWS cortó, vectorizó y guardó los pedazos (lo mismo que mis pasos A2–A4, pero automático).
- La probé en la pantalla **Test** de la consola, primero solo búsqueda y luego búsqueda + respuesta con **Claude Haiku 4.5**.

### Resultados
| Pregunta | Mac (Fase 1) | AWS (Fase 2) |
|---|---|---|
| ¿Cuánto me dan para comida en un viaje nacional? | ✅ $900 MXN | ✅ $900 MXN + fuente |
| ¿Puedo hacer home office? | ⚠️ Incompleta | ✅ Completa (3 oficina / 2 casa, martes y jueves) |
| Vacaciones en la oficina de Francia (no existe) | ✅ "No lo sé" a $0 | ✅ No inventó, pero sí llamó a Claude |

### Qué aprendí
- **Cómo se corta cambia el resultado:** mi Mac cortaba por secciones y perdió el "modelo híbrido"; AWS corta por tamaño y lo dejó junto con el resto. Ninguno es perfecto: hay que medir con el examen.
- **Solo búsqueda vs. búsqueda + respuesta:** la búsqueda siempre trae varios pedazos, aunque algunos no sirvan; Claude filtra.
- **La búsqueda agéntica** solo está en la Managed Knowledge Base. Con la clásica la haré yo con código.
- **La consola usa sus propias instrucciones:** respuestas largas y sin umbral. Mis reglas irán en la Lambda.

### Problemas y cómo los resolví
- **Nombre del bucket con error** → un carácter invisible al pegar; lo escribí a mano.
- **Entré al formulario de Managed KB** → no deja elegir S3 Vectors; usé el flujo clásico.
- **La ruta de S3 apuntaba a todo el bucket** → la corregí a `documentos/`.

### Siguiente
- Crear la **Lambda** que consulta la Knowledge Base y a Claude con mis reglas (5 líneas, citas, umbral 0.30, trazas).
- Ponerle la **API** (`POST /preguntar`) con límite de solicitudes.

---

## Sesión 4: La Lambda del agente (Fase 2)
*13 de octubre de 2026*

### Qué hice
- Escribí `aws/lambda_function.py`: el mismo agente de `preguntar.py`, pero busca en la **Knowledge Base** (`retrieve`) y habla con **Claude Haiku 4.5** por Bedrock (`converse`), sin llaves.
- Creé la Lambda `agente-soporte` (Python 3.14, arm64, 128 MB, timeout de 30 s) con un rol nuevo y vacío.
- Puse `KB_ID` y `UMBRAL` como **variables de entorno**, fuera del código.
- Probé **sin permisos a propósito**: `AccessDeniedException` en `bedrock:Retrieve`. El rol nació sin acceso a nada.
- Le di una política con solo 2 permisos (`aws/politica-iam.json`): buscar en **mi** KB y usar **solo** Claude Haiku 4.5.
- Calibré el umbral del "no lo sé" con datos reales.

### Resultados
| Pregunta | Mejor puntaje | ¿Llamó a Claude? | Costo |
|---|---|---|---|
| ¿Puedo hacer home office? | 0.430 | Sí | $0.0030 |
| ¿Cuánto me dan para comida en un viaje nacional? | 0.436 | Sí | $0.0018 |
| ¿Cuál es la capital de Francia? (umbral 0.30) | 0.356 | Sí, contestó "no lo sé" | $0.0023 |
| ¿Cuál es la capital de Francia? (umbral 0.38) | 0.356 | **No** | **$0** (0.6 s) |

### Qué aprendí
- **Un error a propósito es una prueba:** ver el `AccessDenied` antes de dar permisos confirma el mínimo privilegio. Como probar que el firewall bloquea antes de abrir el puerto.
- **Los puntajes de AWS no se parecen a los de mi Mac:** todos salen pegados (0.35 a 0.44). El 0.30 dejaba pasar todo. Hay que **medir antes de decidir**.
- **Umbral en 0.38, no 0.40:** prefiero que se cuele una pregunta mala ($0.002, y Claude igual dice "no lo sé") a bloquear una buena.
- **Pedazos grandes cuestan más:** en AWS cada pregunta cuesta ~2 veces más que en mi Mac, porque Claude lee pedazos más largos.
- **Variables de entorno:** cambié el umbral sin tocar el código.

### Problemas y cómo los resolví
- **La pantalla de crear Lambda cambió** → ya no dice "Create a new role…". Ahora es el interruptor *Custom execution role*: apagado = rol nuevo.
- **Casi reutilizo el rol del Agente #1** → cada agente lleva su propio rol, con solo sus permisos.

### Siguiente
- Ponerle la **API** (`POST /preguntar`) con límite de solicitudes y probar con `curl`.
- Fase 3: recalibrar el umbral con el examen de 15–20 preguntas. Quitar las negritas (markdown) si la respuesta va a WhatsApp.

---

## Sesión 5: La API, el agente responde desde internet (Fase 2 completa)
*16 de octubre de 2026*

### Qué hice
- Creé un **HTTP API** en API Gateway (`agente-soporte-api`) con la ruta `POST /preguntar` conectada a la Lambda (payload 2.0) y el stage `$default` con auto-deploy.
- No cambié el código: la Lambda ya sabía leer la pregunta dentro de `body`.
- Le puse 2 candados: **2 solicitudes por segundo** (ráfagas de 5) en la API y **2 Lambdas a la vez** (reserved concurrency).
- Probé con `curl` desde mi Mac.

### Resultados
| Prueba | Resultado | Costo |
|---|---|---|
| Comida en viaje nacional | ✅ $900 MXN + fuente | $0.0018 |
| Home office | ✅ Completa + fuente | $0.0030 |
| Capital de Francia | ✅ "No lo sé" sin llamar a Claude | $0 |
| Pregunta vacía | ✅ Error amable con ejemplo | $0 |

### Qué aprendí
- **Respuesta directa vs. segundo plano:** el Agente #1 tarda minutos, por eso responde "ticket" y guarda en S3. Este responde en segundos, así que contesta directo.
- **Una API pública necesita frenos:** cualquiera con el link puede gastar mi dinero. El límite de la API y el de la Lambda son el tope.
- **Las pantallas de AWS cambian:** las rutas ya no vienen prellenadas; hay que darle "Add route".

### Siguiente
- Fase 3: examen de 15–20 preguntas, recalibrar el umbral, quitar el formato markdown y probar la segunda búsqueda de Claude.

---

## Sesión 6: El examen de 20 preguntas (Fase 3)
*16 de octubre de 2026*

### Qué hice
- Escribí `examen_preguntas.json`: **20 preguntas** sacadas de los documentos de Nimbo. 16 con respuesta (varias escritas como habla la gente y una que necesita 2 documentos) y 4 trampas que no están en los documentos.
- Escribí `examen.py`: manda las 20 preguntas a la API y califica solo. Aprueba si cita el documento correcto y menciona el dato clave, o si dice "no lo sé" en las trampas. Guarda el detalle en `salidas/examen_resultados.csv`.
- Mejoré la Lambda: responde también el `mejor_puntaje`, el modelo es variable de entorno (`MODELO`) y quita las negritas (`**`) con código.
- Corrí el examen con el umbral en 0 para ver los 20 puntajes y recalibré el umbral.

### Resultados
| Corrida | Calificación | Costo |
|---|---|---|
| Primera (umbral 0) | 19/20 (el error era del examen, no del agente) | $0.0439 |
| Después de un cambio | 0/20: error 500 por una `e` suelta al pegar el código | $0 |
| Final (umbral 0.37) | **20/20** | **$0.0416** |

| Grupo | Puntajes |
|---|---|
| Preguntas con respuesta (16) | 0.383 a 0.522 |
| Preguntas trampa (4) | Francia 0.356, estacionamiento 0.378, maternidad 0.379, sueldo de gerente **0.459** |

### Qué aprendí
- **El examen también se equivoca:** la pregunta 16 estaba bien contestada (citó `onboarding`, que también lo dice). Hay que leer las respuestas, no solo la calificación.
- **El umbral no separa todo:** "¿Cuánto gana un gerente?" sacó 0.459, más que muchas preguntas buenas. Ningún umbral la bloquea sin bloquear preguntas buenas.
- **Dos candados:** el umbral (0.37) ahorra dinero con lo obvio; Claude, con sus reglas, cuida la verdad con lo difícil. Dijo "no lo sé" en las 4 trampas.
- **El 0.38 era peligroso:** la pregunta de ChatGPT sacó 0.383. Con 3 datos no se ve; con 20 sí.
- **Pedir no basta, hay que asegurar:** Claude a veces ignora "sin negritas", así que el código las quita siempre.
- **Una letra tumba todo:** una `e` suelta dio 20 errores 500. El examen lo detectó en un minuto.

### Problemas y cómo los resolví
- **`examen.py` no se encontraba** → la terminal estaba en `~`; con `cd ~/proyectos/agente-soporte-interno` se arregló.
- **Error 500 en las 20 preguntas** → `NameError: name 'e' is not defined`. Una `e` se coló al pegar el código en la consola (línea 42). La borré y redesplegué.
- **El umbral no se había guardado** → Francia seguía costando dinero. Lo cambié a 0.37 y el costo bajó.

### Siguiente
- Agregar 4–5 preguntas más difíciles (varios documentos, preguntas vagas). Solo si fallan, construir la segunda búsqueda de Claude y medir si las arregla.

