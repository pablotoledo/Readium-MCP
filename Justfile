# Justfile para tareas comunes

# Ejecutar el servidor MCP
run:
    poetry run readium-mcp

# Ejecutar tests
test:
    poetry run pytest

# Linting de código
lint:
    poetry run ruff check .
    poetry run pyright src

# Auto-fix de código
fix:
    poetry run ruff check . --fix

# Ejecutar pre-commit manualmente
pre-commit:
    poetry run pre-commit run --all-files

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
