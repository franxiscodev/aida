import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

class AzureVoiceAdapter:
    """
    Adaptador para convertir texto en audio (TTS) usando Azure Speech Services.
    """
    def __init__(self):
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION", "westeurope")
        
        if not self.speech_key or "your-speech" in self.speech_key:
            # Permitimos inicialización sin config para no romper la app, 
            # pero fallará al intentar sintetizar.
            self.speech_config = None
        else:
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key, 
                region=self.speech_region
            )
            # Seleccionamos una voz natural en español de España
            # Elvira es una voz femenina muy clara para asistentes.
            self.speech_config.speech_synthesis_voice_name = "es-ES-ElviraNeural"

    def speak(self, text: str, output_filename: str = "response_aida.wav") -> str:
        """
        Convierte el texto en un archivo de audio .wav.
        Devuelve la ruta absoluta del archivo generado.
        """
        if self.speech_config is None:
            raise ValueError("Error: AZURE_SPEECH_KEY no configurado en el archivo .env")

        # Asegurar que el directorio de salida existe
        output_dir = os.path.join("data", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Configurar la salida de audio a un archivo
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        
        # Crear el sintetizador
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, 
            audio_config=audio_config
        )

        print(f"Sintetizando voz para: '{text[:50]}...'")
        result = synthesizer.speak_text_async(text).get()

        # Verificar el resultado
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Audio generado con éxito en: {output_path}")
            return os.path.abspath(output_path)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_msg = f"Error de síntesis: {cancellation_details.reason}"
            if cancellation_details.error_details:
                error_msg += f" - Detalles: {cancellation_details.error_details}"
            raise Exception(error_msg)
        
        return output_path
