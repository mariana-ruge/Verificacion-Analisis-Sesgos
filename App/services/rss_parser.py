import feedparser
import httpx
from utils.logger import obtener_logger

logger = obtener_logger(__name__)


class RSSParser:
    """Servicio para extraer artículos de feeds RSS"""

    @staticmethod
    async def fetch_articles(url: str, maximo_articulos: int = 1) -> list[dict]:
        """Extrae artículos de un feed RSS"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as cliente:
                respuesta = await cliente.get(url)
                respuesta.raise_for_status()

            feed = feedparser.parse(respuesta.text)
            articulos = []

            for entrada in feed.entries[:maximo_articulos]:
                articulos.append({
                    "titulo": entrada.get("title", "Sin título"),
                    "contenido": entrada.get(
                        "summary",
                        entrada.get("description", "")
                    ),
                    "enlace": entrada.get("link", ""),
                    "publicado": entrada.get("published", "")
                })

            logger.info(f"Se extrajeron {len(articulos)} artículos de {url}")
            return articulos

        except Exception as error:
            logger.error(f"Error al analizar RSS: {error}")
            raise ValueError(f"No se pudo procesar el feed RSS: {str(error)}")