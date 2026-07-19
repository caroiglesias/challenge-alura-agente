import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuración de página
st.set_page_config(page_title="🤖 Agente BimBam Buy", page_icon="🛒")

st.title("🤖 Agente BimBam Buy")
st.markdown("Haz preguntas sobre políticas de reembolso, envíos, garantías, métodos de pago y programa de afiliados.")

# API Key de Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

if not GOOGLE_API_KEY:
    st.error("❌ No se encontró la API Key de Gemini. Configura la variable de entorno GOOGLE_API_KEY.")
    st.stop()

# Variable de sesión para el agente
if "agente" not in st.session_state:
    st.session_state.agente = None
    st.session_state.documentos_cargados = False

# Función para inicializar el agente (sin cache para evitar problemas de memoria)
def inicializar_agente():
    try:
        # Cargar documentos
        documentos = []
        data_dir = "data"
        
        if os.path.exists(data_dir):
            for archivo in os.listdir(data_dir):
                if archivo.endswith('.pdf'):
                    st.info(f"📄 Cargando: {archivo}")
                    loader = PyPDFLoader(os.path.join(data_dir, archivo))
                    documentos.extend(loader.load())
        
        if not documentos:
            return None
        
        st.info(f"✅ {len(documentos)} páginas cargadas. Procesando...")
        
        # Dividir en chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documentos)
        
        st.info(f"✅ {len(chunks)} chunks creados. Creando embeddings...")
        
        # Crear vectorstore con persistencia en disco
        persist_dir = "./chroma_db"
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        if os.path.exists(persist_dir):
            # Reutilizar vectorstore existente
            vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
            st.info("✅ Base de vectores existente cargada")
        else:
            # Crear nueva
            vectorstore = Chroma.from_documents(
                documents=chunks, 
                embedding=embeddings,
                persist_directory=persist_dir
            )
            vectorstore.persist()
            st.info("✅ Nueva base de vectores creada")
        
        # Crear agente
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3, 
            google_api_key=GOOGLE_API_KEY
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )
        
        return qa_chain
        
    except Exception as e:
        st.error(f"❌ Error al inicializar: {str(e)}")
        return None

# Botón para cargar documentos
if not st.session_state.documentos_cargados:
    st.info("🔄 Cargando documentos y creando base de vectores... (puede tardar unos segundos)")
    
    with st.spinner("Procesando documentos..."):
        st.session_state.agente = inicializar_agente()
        st.session_state.documentos_cargados = True
    
    if st.session_state.agente:
        st.success("✅ Agente cargado correctamente con los documentos de BimBam Buy")
        st.rerun()
    else:
        st.warning("⚠️ No se encontraron documentos PDF en la carpeta `data/`.")
        st.info("""
        **Documentos necesarios:**
        - Política de Reembolsos y Devoluciones
        - Programa de Afiliados
        - Guía de Tiempos y Costos de Envío
        - Preguntas Frecuentes sobre Métodos de Pago
        - Manual de Garantía de Productos
        """)
else:
    # Interfaz de chat
    if st.session_state.agente:
        st.success("✅ Agente listo para responder")
        
        pregunta = st.text_input("💬 Escribe tu pregunta:", placeholder="¿Cuál es la política de reembolsos?")
        
        if pregunta:
            with st.spinner("🤔 Pensando..."):
                try:
                    respuesta = st.session_state.agente({"query": pregunta})
                    
                    st.markdown("### 💡 Respuesta")
                    st.write(respuesta["result"])
                    
                    with st.expander("📚 Ver fuentes utilizadas"):
                        for i, doc in enumerate(respuesta["source_documents"], 1):
                            st.markdown(f"**Fuente {i}:** {os.path.basename(doc.metadata.get('source', 'Desconocida'))}")
                            st.text(doc.page_content[:300] + "...")
                except Exception as e:
                    st.error(f"❌ Error al responder: {str(e)}")
    else:
        # Modo demo sin documentos
        st.markdown("---")
        st.markdown("### 🧪 Modo Demo (sin documentos)")
        
        pregunta_demo = st.text_input("💬 Pregunta a Gemini:", placeholder="¿Qué es BimBam Buy?")
        
        if pregunta_demo:
            with st.spinner("🤔 Pensando..."):
                try:
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash", 
                        temperature=0.3, 
                        google_api_key=GOOGLE_API_KEY
                    )
                    respuesta = llm.invoke(pregunta_demo)
                    st.markdown("### 💡 Respuesta")
                    st.write(respuesta.content)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
