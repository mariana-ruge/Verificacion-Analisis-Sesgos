from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.schemas import SolicitudDebate, RespuestaDebate, TipoEntrada
from services.rss_parser import RSSParser
from services.debate_orchestator import DebateOrchestrator
from utils.logger import obtener_logger
import os
from dotenv import load_dotenv

#Cargar las variables de entorno
load_dotenv()

logger = obtener_logger(__name__)

#Crear el orquestador
orquestador: DebateOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa recursos al iniciar"""
    global orquestador
    token_hf = os.getenv("HUGGINGFACE_TOKEN")
    modelo = os.getenv("MODELO_HF")

    if not token_hf:
        logger.warning(
            "HUGGINGFACE_TOKEN no configurada. "
            "Obtén una gratis en https://huggingface.co/settings/tokens"
        )

    try:
        orquestador = DebateOrchestrator(token_hf=token_hf, modelo=modelo)
        logger.info("API iniciada correctamente")
    except ValueError as error:
        logger.error(f"Error al inicializar: {error}")

    yield
    logger.info("API apagándose")


#Declarar de la API para el debate entre los agentes
app = FastAPI(
    title="API de Debate de Agentes",
    description="API para debate automatizado entre agentes de IA (Hugging Face)",
    version="1.1.0",
    lifespan=lifespan
)

#Crear el CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")

#Definir el origen de las llamadas 
async def root():
    """Endpoint raíz"""
    return {
        "mensaje": "API de Debate de Agentes",
        "version": "1.1.0",
        "proveedor_ia": "Hugging Face",
        "documentacion": "/docs"
    }


@app.get("/health")

#Entender y definir el estado de la API
async def health_check():
    """Verifica estado de la API"""
    return {
        "estado": "saludable",
        "orquestador_configurado": orquestador is not None
    }


@app.post("/debate", response_model=RespuestaDebate, status_code=status.HTTP_200_OK)
async def debate(solicitud: SolicitudDebate):
    """
    Endpoint principal para iniciar el debate entre agentes.
    """
    if orquestador is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de IA no configurado. Verifica HUGGINGFACE_TOKEN."
        )

    try:
        if solicitud.tipo_entrada == TipoEntrada.RSS:
            if not solicitud.url_rss:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="url_rss requerido cuando tipo_entrada es 'rss'"
                )

            articulos = await RSSParser.fetch_articles(
                solicitud.url_rss,
                solicitud.maximo_articulos
            )

            if not articulos:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontraron artículos en el RSS"
                )

            texto = "\n\n".join([
                f"Título: {art['titulo']}\nContenido: {art['contenido']}"
                for art in articulos
            ])
        else:
            if not solicitud.contenido:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="contenido requerido cuando tipo_entrada es 'texto'"
                )
            texto = solicitud.contenido

        resultado = await orquestador.run_debate(texto)
        return resultado

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    except Exception as error:
        logger.error(f"Error en /debate: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

#Crear el entrypoint para el uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)