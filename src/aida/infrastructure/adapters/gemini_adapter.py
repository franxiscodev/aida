import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAdapter:
    """
    Adaptador para el modelo Gemini (Cerebro de AIDA).
    Se encarga de procesar el contexto recuperado y generar respuestas naturales.
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        # Log para verificar la carga de la llave (solo los primeros y últimos caracteres por seguridad)
        if api_key:
            masked_key = f"{api_key[:4]}...{api_key[-4:]}"
            print(f"[DEBUG] GOOGLE_API_KEY cargada: {masked_key}")
        else:
            print("[ERROR] GOOGLE_API_KEY no encontrada en el entorno.")

        if not api_key or "tu-llave" in api_key:
            self.model = None
            print("[WARNING] La GOOGLE_API_KEY parece ser un placeholder o está vacía.")
        else:
            try:
                genai.configure(api_key=api_key)
                # Usamos Gemini 1.5 Flash por su balance entre velocidad y capacidad
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("[DEBUG] Gemini 1.5 Flash inicializado correctamente.")
            except Exception as e:
                self.model = None
                print(f"[ERROR] Error al configurar Gemini: {str(e)}")

    def summarize_definition(self, acronym: str, context: str) -> str:
        """
        Genera una explicación concisa y completa de una sigla basada en el manual.
        """
        if not self.model:
            return f"Definición técnica (Gemini no configurado): {context[:200]}..."

        prompt = (
            f"Eres AIDA, una experta en comercio exterior español. "
            f"Basándote en el siguiente fragmento del Manual del Exportador, explica qué es '{acronym}'.\n\n"
            f"CONTEXTO:\n{context}\n\n"
            f"REGLAS:\n"
            f"1. Responde de forma natural y profesional.\n"
            f"2. IMPORTANTE: Completa siempre las frases y no dejes oraciones a medias.\n"
            f"3. Sé conciso pero asegúrate de que la explicación tenga sentido completo.\n"
            f"4. No uses códigos extraños ni formato markdown complejo."
        )

        try:
            # Aumentamos ligeramente max_output_tokens para evitar cortes abruptos
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=400,
                    temperature=0.3
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error llamando a Gemini: {e}")
            return f"Error procesando la definición de {acronym}."

    def ask_general_question(self, question: str) -> str:
        """
        Responde a preguntas generales sobre AIDA o comercio exterior de forma profesional.
        """
        if not self.model:
            return "Lo siento, mi sistema de inteligencia artificial no está disponible en este momento."

        prompt = (
            f"Eres AIDA, el Asistente Inteligente de Despacho Aduanero. "
            f"El usuario te hace la siguiente consulta: {question}\n\n"
            f"REGLAS:\n"
            f"1. Responde de forma amable, natural y profesional en español.\n"
            f"2. Si te preguntan cómo contactar con un agente, informa que pueden hacerlo a través del soporte técnico oficial.\n"
            f"3. Si la consulta es sobre requisitos de exportación a un país específico, proporciona una respuesta profesional basada en tu conocimiento experto.\n"
            f"4. Si es una pregunta sobre tus funciones, explica brevemente que validas documentos DUA y resuelves dudas técnicas.\n"
            f"5. Completa siempre las frases y no dejes oraciones a medias.\n"
            f"6. No uses markdown ni formato complejo."
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.6
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error en consulta general de Gemini: {e}")
            return "Lo siento, he tenido un problema al procesar tu consulta. ¿Puedo ayudarte con algo referente a un documento DUA?"
