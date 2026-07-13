#Importar los agentes desde el creador
from agents.agent_a import AgentA
from agents.agent_b import AgentB
from models.schemas import RespuestaDebate, RespuestaAgenteA, RespuestaAgenteB
from utils.logger import obtener_logger
import os

logger = obtener_logger(__name__)


class DebateOrchestrator:
    """Orquesta el debate entre los dos agentes"""

    def __init__(self, token_hf: str = None, modelo: str = None):
    #Crear los objetos de los agentes por medio de Hugging Face
        self.token = token_hf or os.getenv("HUGGINGFACE_TOKEN")
        self.modelo = modelo or os.getenv("MODELO_HF")

        self.agent_a = AgentA(token_hf=self.token, modelo=self.modelo)
        self.agent_b = AgentB(token_hf=self.token, modelo=self.modelo)

    async def run_debate(self, texto: str) -> RespuestaDebate:
        """Ejecuta el debate completo entre agentes"""
        try:
            logger.info("Iniciando debate de agentes")

            # Agente A: Identifica afirmaciones
            resultado_agente_a: RespuestaAgenteA = (
                await self.agent_a.analyze(texto)
            )

            # Agente B: Verifica las afirmaciones
            resultado_agente_b: RespuestaAgenteB = (
                await self.agent_b.verify(resultado_agente_a.afirmaciones)
            )

            # Genera veredicto final
            veredicto_final = self._generar_veredicto(
                resultado_agente_a, resultado_agente_b
            )

            #Crear los metadatos de afirmaciones
            metadatos = {
                "total_afirmaciones": len(resultado_agente_a.afirmaciones),
                "afirmaciones_con_verificacion": sum(
                    1 for af in resultado_agente_a.afirmaciones
                    if af.requiere_verificacion
                ),
                "afirmaciones_verificadas": len(resultado_agente_b.verificaciones),
                "modelo_utilizado": self.modelo or "default",
                "proveedor": "Hugging Face Inference API"
            }

            logger.info("Debate completado exitosamente")

            return RespuestaDebate(
                entrada_procesada=(
                    texto[:200] + "..." if len(texto) > 200 else texto
                ),
                hallazgos_agente_a=resultado_agente_a,
                hallazgos_agente_b=resultado_agente_b,
                veredicto_final=veredicto_final,
                metadatos=metadatos
            )

        except Exception as error:
            logger.error(f"Error en orquestación: {error}")
            raise

    def _generar_veredicto(
        self,
        agente_a: RespuestaAgenteA,
        agente_b: RespuestaAgenteB
    ) -> str:
        """Genera veredicto final"""
        if not agente_b.verificaciones:
            return "No se encontraron afirmaciones que requieran verificación."

        verificadas = sum(
            1 for vf in agente_b.verificaciones
            if vf.estado_verificacion == "verificado"
        )
        contradichas = sum(
            1 for vf in agente_b.verificaciones
            if vf.estado_verificacion == "contradicho"
        )
        total = len(agente_b.verificaciones)

        partes = [f"De {total} afirmaciones verificadas:"]

        if verificadas > 0:
            partes.append(f"{verificadas} verificadas")
        if contradichas > 0:
            partes.append(f"{contradichas} contradichas")

        partes.append(f"\nEvaluación general: {agente_b.evaluacion_general}")

        return " ".join(partes)