import sys
import os
import uvicorn

# Agregar el directorio actual al PYTHONPATH
# Esto permite que Python encuentre los módulos: agents, models, services, utils
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"PYTHONPATH configurado: {current_dir}")
print(f"Módulos disponibles: {os.listdir(current_dir)}")

if __name__ == "__main__":
    print("Iniciando FastAPI con uvicorn...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )