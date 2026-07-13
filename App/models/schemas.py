from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TipoEntrada(str, Enum):
    TEXTO = "texto"
    RSS = "rss"


class SolicitudDebate(BaseModel):
    tipo_entrada: TipoEntrada = Field(
        default=TipoEntrada.TEXTO,
        description="Tipo de entrada: 'texto' o 'rss'"
    )
    contenido: Optional[str] = Field(
        default=None,
        description="Texto a analizar (requerido si tipo_entrada es 'texto')"
    )
    url_rss: Optional[str] = Field(
        default=None,
        description="URL del feed RSS (requerido si tipo_entrada es 'rss')"
    )
    maximo_articulos: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Cantidad máxima de artículos a procesar"
    )


class Afirmacion(BaseModel):
    texto: str = Field(description="Texto de la afirmación")
    requiere_verificacion: bool = Field(
        description="Indica si requiere verificación"
    )
    confianza: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Nivel de confianza (0 a 1)"
    )


class VerificacionHecho(BaseModel):
    afirmacion: str = Field(description="Afirmación verificada")
    fuentes: List[str] = Field(
        default_factory=list,
        description="Fuentes consultadas"
    )
    sesgo_detectado: Optional[str] = Field(
        default=None,
        description="Sesgo detectado, si existe"
    )
    estado_verificacion: str = Field(
        description="Estado de verificación"
    )
    confianza: float = Field(
        default=0.5,
        ge=0,
        le=1,
        description="Confianza de la verificación"
    )


class RespuestaAgenteA(BaseModel):
    afirmaciones: List[Afirmacion]
    resumen: str


class RespuestaAgenteB(BaseModel):
    verificaciones: List[VerificacionHecho]
    evaluacion_general: str


class RespuestaDebate(BaseModel):
    entrada_procesada: str
    hallazgos_agente_a: RespuestaAgenteA
    hallazgos_agente_b: RespuestaAgenteB
    veredicto_final: str
    metadatos: dict