import logging
import sys
from typing import Optional


def obtener_logger(nombre: str, nivel: Optional[str] = None) -> logging.Logger:
    """Configura y retorna un logger"""
    logger = logging.getLogger(nombre)

    if not logger.handlers:
        manejador = logging.StreamHandler(sys.stdout)
        formateador = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        manejador.setFormatter(formateador)
        logger.addHandler(manejador)

    logger.setLevel(nivel or logging.INFO)
    return logger