import uuid
import random
import string
import logging
from typing import Literal
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# Configuración básica de logging para visualizar en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Ventas - APU Manager PRO",
    description="API para procesar pagos y despachar licencias de APU Manager PRO.",
    version="1.0.0"
)

# ---------------------------------------------------------
# 1. Modelos (Pydantic)
# ---------------------------------------------------------

class CheckoutRequest(BaseModel):
    preference: Literal["email"] = Field(
        ..., 
        description="La licencia se entrega por correo electrónico"
    )
    contactValue: str = Field(
        ..., 
        description="Dirección de correo electrónico del cliente",
        min_length=3
    )

class PaymentWebhook(BaseModel):
    referencia_pago: str = Field(..., description="ID único de la transacción de prueba")
    contacto: str = Field(..., description="Contacto del cliente asociado al pago")
    metodo_entrega: Literal["email"] = Field(
        "email", 
        description="Entrega exclusiva por correo electrónico"
    )

# ---------------------------------------------------------
# 3. Generación de Licencia y Envío
# ---------------------------------------------------------

def generar_licencia() -> str:
    """Genera una licencia alfanumérica aleatoria con formato APU-XXXX-XXXX-XXXX."""
    def random_segment(length=4):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    return f"APU-{random_segment()}-{random_segment()}-{random_segment()}"

async def enviar_licencia(contacto: str, preferencia: str, licencia: str):
    """
    Simula el envío de la licencia al cliente a través del medio seleccionado.
    Esta tarea está pensada para ejecutarse en segundo plano (BackgroundTasks).
    """
    # En un entorno real, aquí se integraría la API de Twilio, SendGrid, etc.
    mensaje = f"Enviando licencia {licencia} a {contacto} vía {preferencia}"
    logger.info(f"*** {mensaje} ***")


# ---------------------------------------------------------
# 2. Endpoint de Checkout (POST /checkout)
# ---------------------------------------------------------

@app.post("/checkout", status_code=200)
async def process_checkout(request: CheckoutRequest):
    """
    Recibe los datos del cliente, genera una sesión de pago única y 
    retorna un link de pago simulado.
    """
    try:
        # Generar un identificador único para esta intención de compra
        session_id = str(uuid.uuid4())
        
        # Aquí se consumiría el endpoint de Wompi / MercadoPago en la vida real
        payment_url = f"https://checkout.wompi.co/simulacion/{session_id}"
        
        logger.info(f"Sesión de checkout creada: {session_id} para {request.contactValue}")
        
        return {
            "session_id": session_id,
            "init_point": payment_url
        }
    except Exception as e:
        logger.error(f"Error procesando checkout: {e}")
        raise HTTPException(status_code=400, detail="Error al procesar la solicitud de checkout")


# ---------------------------------------------------------
# 4. Webhook de Confirmación (POST /webhook/payment)
# ---------------------------------------------------------

@app.post("/webhook/pago-exitoso", status_code=200)
async def payment_webhook(webhook_data: PaymentWebhook, background_tasks: BackgroundTasks):
    """
    Endpoint (Webhook) que recibe la notificación de pago simulada desde el frontend.
    Genera y despacha la licencia en segundo plano.
    """
    logger.info(f"Webhook recibido para transacción: {webhook_data.referencia_pago}")
    
    # Como es una simulación directa desde el frontend, asumimos pago aprobado.
    nueva_licencia = generar_licencia()
    
    # Agregamos la tarea de envío a segundo plano
    background_tasks.add_task(
        enviar_licencia, 
        contacto=webhook_data.contacto, 
        preferencia=webhook_data.metodo_entrega, 
        licencia=nueva_licencia
    )
        
    # Retornamos los datos para que el frontend los muestre en el mensaje de éxito
    return {
        "status": "ok", 
        "licencia": nueva_licencia, 
        "contacto": webhook_data.contacto
    }
