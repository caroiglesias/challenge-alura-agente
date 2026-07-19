import os
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
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

# Inicializar el agente (con cache para no recargar cada vez)
@st.cache_resource
def inicializar_agente():
    # Cargar documentos
    documentos = []
    data_dir = "data"
    
    if os.path.exists(data_dir):
        for archivo in os.listdir(data_dir):
            if archivo.endswith('.pdf'):
                loader = PyPDFLoader(os.path.join(data_dir, archivo))
                documentos.extend(loader.load())
    
    if not documentos:
        st.error("❌ No se encontraron documentos PDF en la carpeta data/")
        st.stop()
    
    # Dividir en chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documentos)
    
    # Crear vectorstore
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    
    # Crear agente
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, google_api_key=GOOGLE_API_KEY)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    
    return qa_chain

# Interfaz de chat
try:
    agente = inicializar_agente()
    st.success("✅ Agente cargado correctamente")
    
    pregunta = st.text_input("💬 Escribe tu pregunta:", placeholder="¿Cuál es la política de reembolsos?")
    
    if pregunta:
        with st.spinner("🤔 Pensando..."):
            respuesta = agente({"query": pregunta})
        
        st.markdown("### 💡 Respuesta")
        st.write(respuesta["result"])
        
        with st.expander("📚 Ver fuentes utilizadas"):
            for i, doc in enumerate(respuesta["source_documents"], 1):
                st.markdown(f"**Fuente {i}:** {os.path.basename(doc.metadata.get('source', 'Desconocida'))}")
                st.text(doc.page_content[:300] + "...")
                
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
