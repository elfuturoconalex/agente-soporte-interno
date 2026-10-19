# ADR 001: Vector store para la base de conocimiento en AWS

- **Estado:** Aceptado
- **Fecha:** 11 de octubre de 2026
- **Autor:** Alejandro Padilla

## 1. Contexto

El Agente de Soporte Interno ya funciona en local (Fase 1): los documentos se cortan en pedazos, se convierten en vectores y se guardan en un archivo en mi Mac. En la Fase 2 el agente pasa a AWS con **Amazon Bedrock Knowledge Bases**, y hay que decidir **dónde se guardan los vectores** (el vector store).

## 2. Requisitos (lo que me importa)

| # | Requisito | Peso |
|---|---|---|
| R1 | **Costo:** proyecto personal de aprendizaje; presupuesto total de 5 a 10 USD y alarma en 5 USD. No puede haber un costo fijo mensual aunque nadie lo use. | Muy alto |
| R2 | **Volumen:** 7 documentos, ~50 pedazos. Podría crecer a cientos, no a millones. | Medio |
| R3 | **Tráfico:** pocas preguntas al día (pruebas y examen). | Bajo |
| R4 | **Latencia:** responder en pocos segundos es suficiente; no se necesitan milisegundos. | Bajo |
| R5 | **Simplicidad:** que se cree y se borre fácil (y después con Terraform). | Alto |
| R6 | **Integración:** que Bedrock Knowledge Bases lo conecte de forma directa. | Alto |
| R7 | **Aprendizaje:** aprender tecnología nueva y relevante para mi carrera. | Medio |
| R8 | **Calidad de búsqueda:** la pregunta "¿Puedo hacer home office?" falló con búsqueda solo por significado; la búsqueda híbrida (significado + palabras) podría ayudar. | Medio |

## 3. Opciones consideradas

### A. Amazon S3 Vectors
"La bodega barata": almacenamiento de S3 diseñado para vectores.
- **Costo:** se paga por lo que se guarda y se consulta; **sin costo fijo**. Para ~50 pedazos, centavos al mes.
- **Latencia:** del orden de 50 a 200 ms por búsqueda. Suficiente para este caso.
- **A favor:** la más barata y la más sencilla; servicio nuevo de AWS (relevante para aprender).
- **En contra:** sin búsqueda híbrida (solo por significado); menos funciones avanzadas.

### B. Amazon OpenSearch Serverless
"El buscador profesional".
- **Costo:** se cobra por capacidad (OCU, ~0.24 USD por hora). En su modo clásico necesita **al menos 2 OCU** aunque nadie lo use: **~350 USD al mes**. AWS anunció una nueva generación que puede bajar a cero sin uso, pero hay que confirmar su disponibilidad y su integración con Bedrock.
- **Latencia:** muy baja (milisegundos).
- **A favor:** búsqueda híbrida, filtros avanzados; el estándar para RAG empresarial de alto tráfico.
- **En contra:** el costo fijo rompe el requisito R1 (sería ~35 a 70 veces el presupuesto total en un solo mes).

### C. Amazon Aurora PostgreSQL Serverless v2 con pgvector
"La base de datos tradicional que aprendió vectores".
- **Costo:** se cobra por capacidad (ACU). Desde finales de 2024 puede **pausarse en 0 ACU** sin uso, pero al reactivarse tarda unos segundos en la primera consulta; también hay costo de almacenamiento.
- **A favor:** SQL + vectores en un solo lugar; ideal si la empresa ya tiene datos en PostgreSQL.
- **En contra:** más piezas que configurar (clúster, VPC, credenciales en Secrets Manager); demasiado para ~50 pedazos.

### Otras opciones descartadas
- **DynamoDB, DocumentDB, MemoryDB, Neptune:** también guardan vectores, pero no son la integración más directa con Bedrock Knowledge Bases para este caso, o están pensadas para otros patrones (latencia de microsegundos, grafos).
- **Mantener el vector store local:** no cumple el objetivo de la Fase 2 (correr en AWS).

## 4. Comparación

| Criterio | S3 Vectors | OpenSearch Serverless | Aurora + pgvector |
|---|---|---|---|
| R1 Costo sin uso | ✅ ~0 | ❌ ~350 USD/mes (clásico) | ⚠️ ~0 pausado + almacenamiento |
| R2 Volumen | ✅ | ✅ | ✅ |
| R3/R4 Tráfico y latencia | ✅ suficiente | ✅ la mejor | ⚠️ arranque lento al reactivarse |
| R5 Simplicidad | ✅ alta | ⚠️ media | ❌ baja |
| R6 Integración con Bedrock | ✅ | ✅ | ✅ |
| R7 Aprendizaje | ✅ servicio nuevo | ✅ estándar del mercado | ✅ SQL + vectores |
| R8 Búsqueda híbrida | ❌ | ✅ | ⚠️ posible, con más trabajo |

## 5. Decisión

**Elijo Amazon S3 Vectors** como vector store de la Bedrock Knowledge Base.

Es la única opción que cumple el requisito más importante (R1: sin costo fijo mensual), además de ser la más sencilla (R5), conectarse directo con Bedrock (R6) y ser un servicio nuevo de AWS (R7). Su latencia (50 a 200 ms) es más que suficiente para este caso (R4).

## 6. Consecuencias

### Qué gano
- Costo de centavos al mes para el volumen del proyecto, y ningún cobro si nadie lo usa.
- Menos piezas que configurar y que borrar (sin clúster, sin VPC, sin credenciales de base de datos).

### Qué sacrifico
- **No hay búsqueda híbrida** (significado + palabras). La pregunta "¿Puedo hacer home office?" ya mostró este límite.

### Cómo cubro esa debilidad (con software, no con infraestructura)
- **Segunda búsqueda de Claude (RAG agéntico):** si los pedazos no responden completa la pregunta, Claude la reescribe con otras palabras (por ejemplo, "trabajo remoto, días en casa") y busca de nuevo, con un máximo de 2 o 3 búsquedas. Se medirá con el examen: aciertos, costo y tiempo, con y sin segunda búsqueda.

### Prueba de comparación planeada
- Al final del proyecto, **un día dedicado a OpenSearch Serverless**: crearlo, correr el mismo examen y **borrarlo el mismo día** (incluida la colección de OpenSearch, que no se borra sola al borrar la Knowledge Base). Costo estimado: 1 a 2 USD por unas horas (~0.24 a 0.48 USD por hora). Así la decisión queda respaldada con datos y no solo en papel.

### Cuándo cambiaría de opinión
- Si el tráfico creciera a cientos de preguntas por minuto o se necesitaran respuestas en milisegundos → **OpenSearch Serverless**.
- Si la búsqueda híbrida resultara indispensable y la segunda búsqueda no alcanzara en el examen → **OpenSearch Serverless**.
- Si la empresa ya tuviera sus datos en PostgreSQL y quisiera todo en un solo lugar → **Aurora + pgvector**.

## 7. Seguimiento: resultado con datos (Fase 3, octubre 2026)

- **Examen automático de 25 preguntas** (16 normales, 5 difíciles y 4 trampas) contra el agente en AWS: **25/25**.
- **La búsqueda sin híbrida fue suficiente.** "¿Puedo hacer home office?" contesta completo en AWS: el corte por tamaño de la Knowledge Base dejó el modelo híbrido junto con los requisitos.
- **La única falla del examen (24/25) no fue de búsqueda:** en "Quiero trabajar 3 semanas desde España" la búsqueda trajo el pedazo correcto, pero Claude fue demasiado precavido y empezó con "no lo sé". Se arregló **ajustando las instrucciones** (responder lo que sí dicen los fragmentos y razonar con los datos), no buscando más.
- **Decisión: la segunda búsqueda de Claude NO se implementa por ahora.** Ninguna pregunta del examen la necesita. Se reconsidera si una pregunta futura falla porque la búsqueda no trae el pedazo correcto.
- **S3 Vectors se mantiene.**

## 8. Fuentes

- AWS: Amazon Aurora Serverless v2 supports scaling to zero capacity (noviembre 2024).
- FactualMinds: Amazon S3 Vectors native vector storage; Bedrock Knowledge Base cost optimization 2026.
- AWS Database Blog: Key considerations when choosing a database for your generative AI applications.
- Los precios cambian: confirmar en la página de precios de AWS antes de crear recursos.
