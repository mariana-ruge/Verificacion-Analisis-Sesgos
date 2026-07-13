import json
from huggingface_hub import AsyncInferenceClient
from models.schemas import RespuestaAgenteA, Afirmacion
from utils.logger import obtener_logger
import os

logger = obtener_logger(__name__)


class AgentA:
    """Agente que identifica afirmaciones que necesitan validación"""

    def __init__(self, token_hf: str = None, modelo: str = None):
        self.token = token_hf or os.getenv("HUGGINGFACE_TOKEN")
        self.modelo = modelo or os.getenv(
            "MODELO_HF",
            "meta-llama/Llama-3.3-70B-Instruct"
        )

        if not self.token:
            raise ValueError(
                "Token de Hugging Face no configurado. "
                "Obtén uno gratis en https://huggingface.co/settings/tokens"
            )

        self.cliente = AsyncInferenceClient(
            provider="hf-inference",
            token=self.token
        )

        self.prompt_sistema = """Eres un analista crítico experto en identificar afirmaciones que requieren verificación.

#Prompts para el cliente

#Tareas del cliente

Tu tarea:
1. Leer el texto proporcionado
2. Identificar afirmaciones factuales verificables
3. Determinar si necesitan verificación externa
4. Asignar nivel de confianza

Responde SOLO con JSON válido en este formato:
{
  "afirmaciones": [
    {
      "texto": "la afirmación",
      "requiere_verificacion": true,
      "confianza": 0.85
    }
  ],
  "resumen": "resumen del análisis"
}"""

    async def analyze(self, texto: str) -> RespuestaAgenteA:
        """Analiza el texto y extrae afirmaciones"""
        try:
            mensaje = f"Analiza este texto:\n\n{texto}"

            respuesta = await self.cliente.chat.completions(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": self.prompt_sistema},
                    {"role": "user", "content": mensaje}
                ],
                temperature=0.3,
                max_tokens=2048
            )

            contenido = respuesta.choices[0].message.content

            # Extraer JSON
            if "```json" in contenido:
                inicio = contenido.find("```json") + 7
                fin = contenido.find("```", inicio)
                contenido = contenido[inicio:fin].strip()
            elif "```" in contenido:
                inicio = contenido.find("```") + 3
                fin = contenido.find("```", inicio)
                contenido = contenido[inicio:fin].strip()

            resultado = json.loads(contenido)

            afirmaciones = [
                Afirmacion(
                    texto=af.get("texto", ""),
                    requiere_verificacion=af.get("requiere_verificacion", False),
                    confianza=float(af.get("confianza", 0.5))
                )
                for af in resultado.get("afirmaciones", [])
            ]

            logger.info(f"Agente A identificó {len(afirmaciones)} afirmaciones")
            return RespuestaAgenteA(
                afirmaciones=afirmaciones,
                resumen=resultado.get("resumen", "Análisis completado")
            )

        except Exception as error:
            logger.error(f"Error en Agente A: {error}")
            raise