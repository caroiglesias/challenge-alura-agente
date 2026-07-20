import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

# Configuración de página
st.set_page_config(page_title="🤖 Agente BimBam Buy", page_icon="🛒")

st.title("🤖 Agente BimBam Buy")
st.markdown("Haz preguntas sobre políticas de reembolso, envíos, garantías, métodos de pago y programa de afiliados.")

# API Key de Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

if not GOOGLE_API_KEY:
    st.error("❌ No se encontró la API Key de Gemini.")
    st.stop()

# Contexto de BimBam Buy (resumen de los documentos)
CONTEXTO_BIMBAM = """
Eres un agente de atención al cliente de BimBam Buy, un e-commerce multiplataforma.
Responde preguntas basándote en la siguiente información:

**Política de Reembolsos y Devoluciones:**
- Los clientes tienen 30 días para devolver productos desde la fecha de recepción.
- Los productos deben estar en su empaque original y sin usar.
- Los reembolsos se procesan en 5-10 días hábiles.
- Los gastos de envío de devolución corren por cuenta del cliente, excepto si el producto llegó defectuoso.
- Para iniciar una devolución, contactar a soporte@bimbambuy.com.

**Programa de Afiliados:**
- Comisión del 10% por cada venta generada.
- Pagos mensuales vía transferencia bancaria o PayPal.
- Mínimo de $50 para retirar comisiones.
- Acceso a panel de control con estadísticas en tiempo real.
- Soporte dedicado para afiliados.

**Métodos de Pago Aceptados:**
- Tarjetas de crédito y débito (Visa, Mastercard, American Express).
- PayPal.
- Transferencia bancaria.
- Pago contra entrega (solo en ciertas zonas).
- Mercado Pago (Latinoamérica).

**Tiempos y Costos de Envío:**
- Envío estándar: 5-7 días hábiles, costo variable según zona.
- Envío express: 2-3 días hábiles, costo mayor.
- Envío gratis en compras mayores a $500.
- Envíos internacionales: 10-15 días hábiles.
- Seguimiento de pedidos disponible 24/7.

**Garantía de Productos:**
- Garantía de 1 año en todos los productos electrónicos.
- Garantía de 6 meses en accesorios.
- Cubre defectos de fabricación, no daños por mal uso.
- Para hacer válida la garantía, presentar factura de compra.
- Servicio técnico disponible en centros autorizados.
"""

# Inicializar Gemini
@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

# Interfaz de chat
try:
    llm = get_llm()
    st.success("✅ Agente BimBam Buy listo para responder")
    
    pregunta = st.text_input("💬 Escribe tu pregunta:", placeholder="¿Cuál es la política de reembolsos?")
