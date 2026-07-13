import json
from huggingface_hub import AsyncInferenceClient
from models.schemas import RespuestaAgenteB, VerificacionHecho, Afirmacion
from utils.logger import obtener_logger
import os

#Obtener logs del cliente

logger = obtener_logger(__name__)


class AgentB:
    """Agente que verifica afirmaciones buscando fuentes y sesgos"""

    def __init__(self, token_hf: str = None, modelo: str = None):
        self.token = token_hf or os.getenv("HUGGINGFACE_TOKEN")
        self.modelo = modelo or os.getenv(
            "MODELO_HF",
            "meta-llama/Llama-3.3-70B-Instruct"
        )

        if not self.token:
            raise ValueError("Token de Hugging Face no configurado")

        self.cliente = AsyncInferenceClient(
            provider="hf-inference",
            token=self.token
        )

        self.prompt_sistema = """Eres un verificador de hechos experto.

Tu tarea:
1. Verificar las afirmaciones proporcionadas
2. Indicar fuentes confiables
3. Identificar posibles sesgos
4. Determinar estado de verificación

Estados: "verificado", "no_verificado", "contradicho", "parcialmente_verificado"

Responde SOLO con JSON válido:
{
  "verificaciones": [
    {
      "afirmacion": "la afirmación",
      "fuentes": ["fuente1"],
      "sesgo_detectado": null,
      "estado_verificacion": "verificado",
      "confianza": 0.88
    }
  ],
  "evaluacion_general": "evaluación general"
}"""

    async def verify(self, afirmaciones: list[Afirmacion]) -> RespuestaAgenteB:
        """Verifica las afirmaciones"""
        try:
            afirmaciones_a_verificar = [
                af for af in afirmaciones if af.requiere_verificacion
            ]

            if not afirmaciones_a_verificar:
                return RespuestaAgenteB(
                    verificaciones=[],
                    evaluacion_general=(
                        "No se identificaron afirmaciones que requieran verificación."
                    )
                )

            texto_afirmaciones = "\n".join([
                f"- {af.texto}" for af in afirmaciones_a_verificar
            ])

            mensaje = f"Verifica estas afirmaciones:\n\n{texto_afirmaciones}"

            respuesta = await self.cliente.chat.completions(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": self.prompt_sistema},
                    {"role": "user", "content": mensaje}
                ],
                temperature=0.2,
                max_tokens=3000
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

            verificaciones = [
                VerificacionHecho(
                    afirmacion=vf.get("afirmacion", ""),
                    fuentes=vf.get("fuentes", []),
                    sesgo_detectado=vf.get("sesgo_detectado"),
                    estado_verificacion=vf.get(
                        "estado_verificacion",
                        "no_verificado"
                    ),
                    confianza=float(vf.get("confianza", 0.5))
                )
                for vf in resultado.get("verificaciones", [])
            ]

            logger.info(f"Agente B verificó {len(verificaciones)} afirmaciones")
            return RespuestaAgenteB(
                verificaciones=verificaciones,
                evaluacion_general=resultado.get(
                    "evaluacion_general",
                    "Verificación completada"
                )
            )

        except Exception as error:
            logger.error(f"Error en Agente B: {error}")
            raise