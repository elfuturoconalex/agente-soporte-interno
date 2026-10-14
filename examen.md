# Examen del agente (Fase 3)

Lista de preguntas para medir al agente. Cada una tiene la respuesta correcta y el pedazo que la búsqueda debería traer.
Se irá llenando durante el proyecto; en la Fase 3 llegará a 15–20 preguntas.

| # | Pregunta | Respuesta esperada | Pedazo que debe traer | Mac (Fase 1) | AWS Knowledge Base (Fase 2) |
|---|---|---|---|---|---|
| 1 | ¿Cuántos días de vacaciones tengo si llevo 2 años? | 14 días | politica-vacaciones-2 | ✅ Correcta | Pendiente |
| 2 | ¿Cuánto me dan para comida en un viaje nacional? | $900 MXN por día | viaticos-y-gastos-3 | ✅ Correcta | ✅ $900 MXN + fuente |
| 3 | ¿Cuál es la capital de Francia? | "No lo sé" (no está en los documentos) | ninguno | ✅ "No lo sé" | Pendiente (se probó "vacaciones en la oficina de Francia": ✅ no inventó) |
| 4 | ¿Puedo hacer home office? | Sí: 3 días en oficina y 2 en casa; martes y jueves en oficina | trabajo-remoto-2 | ⚠️ Incompleta: no dijo cuántos días | ✅ Completa: 3 y 2, martes y jueves |

## Nota sobre la Fase 2
- AWS corta por **tamaño** (~300 tokens), no por secciones. En documentos cortos, el "modelo híbrido" quedó en el mismo pedazo que los requisitos, por eso respondió completo.
- En la pantalla de pruebas de AWS las respuestas salen **largas** y **siempre se llama a Claude** (no hay umbral). La Lambda usará mis reglas: máximo 5 líneas, citas y umbral 0.30.

## Puntajes en AWS (Sesión 4)
Umbral del "no lo sé" en la Lambda: **0.38** (entre 0.356 de la pregunta sin relación y 0.43 de las buenas). Recalibrar en la Fase 3 con más preguntas.

| Pregunta | Mejor puntaje AWS |
|---|---|
| ¿Cuánto me dan para comida en un viaje nacional? | 0.436 |
| ¿Puedo hacer home office? | 0.430 |
| ¿Cuál es la capital de Francia? | 0.356 |

## Comparaciones planeadas
- Con y sin **segunda búsqueda de Claude** (RAG agéntico).
- **S3 Vectors vs. OpenSearch Serverless**: un día dedicado, creando y borrando OpenSearch el mismo día.
