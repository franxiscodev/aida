import os
import shutil
import zipfile
from datetime import datetime

def export_project():
    """
    Limpia archivos temporales y prepara un .zip con el código del proyecto AIDA.
    """
    project_name = "AIDA_Asistente_Aduanero"
    timestamp = datetime.now().strftime("%Y%m%d")
    output_zip = f"{project_name}_{timestamp}.zip"
    
    # 1. Limpiar carpeta de salida de audios
    output_dir = os.path.join("data", "output")
    if os.path.exists(output_dir):
        print(f"Limpiando carpeta de salida: {output_dir}...")
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"No se pudo borrar {file_path}: {e}")

    # 2. Crear el archivo ZIP
    print(f"Empaquetando proyecto en {output_zip}...")
    
    # Carpetas y archivos a excluir
    exclude_dirs = {".git", ".venv", "__pycache__", ".pytest_cache", "data/vector_db", ".gemini"}
    exclude_files = {output_zip, ".env"} # .env suele excluirse por seguridad

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Filtrar carpetas excluidas
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files or file.endswith(".zip"):
                    continue
                
                file_path = os.path.join(root, file)
                # Guardar con ruta relativa limpia
                zipf.write(file_path, arcname=os.path.relpath(file_path, "."))

    print("\n" + "="*40)
    print("SUCCESS: EXPORTACION COMPLETADA")
    print(f"Archivo: {output_zip}")
    print("="*40)

if __name__ == "__main__":
    export_project()
