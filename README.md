# Agente de Soporte Interno (RAG) 🤖📚

Agente de IA que responde preguntas de un equipo consultando su base de conocimiento (políticas, manuales y preguntas frecuentes). **Siempre cita la fuente** de donde sacó la respuesta y, si no la encuentra, responde **"no lo sé"** en lugar de inventar.

> Los documentos son de una **empresa ficticia**, creados solo para este proyecto.

## Fases del proyecto

- [ ] **Fase 1:** Agente local: documentos en archivos, vector store local y respuestas con fuentes
- [ ] **Fase 2:** En AWS: S3 + Bedrock Knowledge Base + vector store + Lambda + API Gateway (con ADR de la decisión)
- [ ] **Fase 3:** Confiabilidad: "no lo sé", citas obligatorias y examen de preguntas
- [ ] **Opcional:** Infraestructura con Terraform

## Arquitectura (preliminar)

![Arquitectura preliminar del agente de soporte interno](docs/agente2-arquitectura-preliminar.png)

**Ingesta (A1–A4):** los documentos se suben a S3, se cortan en pedazos, se convierten en vectores y se guardan en el vector store.

**Consulta (1–7):** el agente busca los pedazos más parecidos a la pregunta, Claude responde solo con ellos y cita sus fuentes.

## Qué demuestra este proyecto

- Qué es RAG y cómo evita que el modelo invente respuestas.
- Cómo se ingesta la documentación (chunking + embeddings).
- Qué es un vector store.
- Toma de decisiones de arquitectura con base en requerimientos (costo, latencia, escala), documentada en un ADR.

## Proyecto anterior

[Agente Investigador](https://github.com/elfuturoconalex/agente-investigador): agente que investiga en la web y deja informes en S3, con observabilidad y Amazon Bedrock.
