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
        if not api_key or "tu-llave" in api_key:
            self.model = None
            print("[WARNING] GOOGLE_API_KEY no configurada. Gemini no estará disponible.")
        else:
            genai.configure(api_key=api_key)
            # Usamos Gemini 1.5 Flash por su balance entre velocidad y capacidad
            self.model = genai.GenerativeModel('gemini-1.5-flash')

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
