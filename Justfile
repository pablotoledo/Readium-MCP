# Justfile para tareas comunes

# Ejecutar el servidor MCP
run:
    poetry run readium-mcp

# Ejecutar tests
test:
    poetry run pytest

# Ejecutar cliente de prueba
test-client:
    poetry run python test.py

# Instalar dependencias
install:
    poetry install

# Actualizar dependencias
update:
    poetry update

# Limpiar archivos temporales
clean:
    rm -rf __pycache__
    rm -rf .pytest_cache
    rm -rf dist
    rm -rf build

# Limpiar y reiniciar proceso
clean-start:
    pkill -f "python -m src.server" || true
    pkill -f "uvicorn" || true
    sleep 2
    poetry run readium-mcp
