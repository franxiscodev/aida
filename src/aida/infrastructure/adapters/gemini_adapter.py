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
                # Configuramos instrucciones de sistema para forzar el comportamiento de AIDA
                self.model = genai.GenerativeModel(
                    model_name='models/gemini-flash-latest',
                    system_instruction=(
                        "Eres AIDA, el Asistente Inteligente de Despacho Aduanero. "
                        "Tu tono es técnico, profesional y extremadamente directo. "
                        "REGLAS DE ORO: "
                        "1. NUNCA te presentes ni digas tu nombre. "
                        "2. NUNCA saludes (nada de 'Hola', 'Buenos días', etc.). "
                        "3. Ve directamente a la información técnica sin introducciones. "
                        "4. Completa siempre todas las frases y oraciones."
                    )
                )
                print("[DEBUG] Gemini Flash (Latest) inicializado con System Instruction.")
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
            f"Define qué es '{acronym}' basándote exclusivamente en este fragmento del Manual del Exportador.\n\n"
            f"CONTEXTO:\n{context}\n\n"
            f"REGLAS CRÍTICAS:\n"
            f"1. No te presentes ni digas 'Soy AIDA'. Ve directo a la definición.\n"
            f"2. Completa siempre las frases y no dejes oraciones a medias.\n"
            f"3. Responde de forma técnica pero natural para un despacho aduanero.\n"
            f"4. Si la información no está en el contexto, indica que no se especifica en el manual."
        )

        try:
            # Aumentamos max_output_tokens a 500 para evitar cortes abruptos
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
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
            f"Consulta del usuario: {question}\n\n"
            f"REGLAS:\n"
            f"1. Responde de forma técnica y profesional en español.\n"
            f"2. Si preguntan por contacto, menciona el soporte técnico oficial.\n"
            f"3. Si es sobre requisitos de exportación, usa tu conocimiento experto.\n"
            f"4. Ve directo al grano, sin saludos ni introducciones.\n"
            f"5. No uses markdown ni formato complejo."
        )

        try:
            # Aumentamos max_output_tokens a 500 para evitar cortes abruptos
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.6
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error en consulta general de Gemini: {e}")
            return "Lo siento, he tenido un problema al procesar tu consulta. ¿Puedo ayudarte con algo referente a un documento DUA?"
