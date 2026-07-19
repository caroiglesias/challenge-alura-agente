# 🤖 Agente BimBam Buy - Challenge Alura Agente

Agente de inteligencia artificial con RAG (Retrieval-Augmented Generation) 
para responder preguntas sobre la documentación de BimBam Buy.

## 📋 Descripción del Proyecto

BimBam Buy es un e-commerce multiplataforma. Este agente permite a cualquier 
persona hacer preguntas sobre políticas de reembolso, envíos, garantías, 
métodos de pago y programa de afiliados sin necesidad de abrir los documentos.

## 🏗️ Arquitectura

- **Carga de documentos**: PyPDFLoader
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2) - Gratis
- **Vector Store**: ChromaDB
- **LLM**: Google Gemini 1.5 Flash - Gratis
- **Framework**: LangChain

## 📁 Estructura del Proyecto
