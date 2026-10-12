# Examen del agente (Fase 3)

Lista de preguntas para medir al agente. Cada una tiene la respuesta correcta y el pedazo que la búsqueda debería traer.
Se irá llenando durante el proyecto; en la Fase 3 llegará a 15–20 preguntas.

| # | Pregunta | Respuesta esperada | Pedazo que debe traer | Resultado actual |
|---|---|---|---|---|
| 1 | ¿Cuántos días de vacaciones tengo si llevo 2 años? | 14 días | politica-vacaciones-2 | ✅ Correcta |
| 2 | ¿Cuánto me dan para comida en un viaje nacional? | $900 MXN por día | viaticos-y-gastos-3 | ✅ Correcta |
| 3 | ¿Cuál es la capital de Francia? | "No lo sé" (no está en los documentos) | ninguno | ✅ "No lo sé" |
| 4 | ¿Puedo hacer home office? | Sí: 3 días en oficina y 2 en casa; martes y jueves en oficina | trabajo-remoto-2 | ⚠️ Incompleta: no dijo cuántos días |

## Comparaciones planeadas
- Con y sin **segunda búsqueda de Claude** (RAG agéntico).
- **S3 Vectors vs. OpenSearch Serverless**: un día dedicado, creando y borrando OpenSearch el mismo día.
