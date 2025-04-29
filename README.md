# Readium MCP

Este proyecto incluye un servidor [FastMCP](https://modelcontextprotocol.io) de ejemplo integrado con Poetry.

## Requisitos

- Python 3.10 o superior
- [Poetry](https://python-poetry.org/)

## Requisitos de desarrollo

- [just](https://just.systems/) — Utilidad para automatizar tareas de desarrollo.
  - En macOS:  
    ```bash
    brew install just
    ```
  - En otros sistemas, consulta la [documentación oficial](https://just.systems/man/en/#installation).
- [uvicorn](https://www.uvicorn.org/) y [starlette](https://www.starlette.io/) — Necesarios para exponer el servidor HTTP en el puerto 8000.
    ```bash
    poetry add --group dev uvicorn starlette
    ```

## Instalación de dependencias

```bash
poetry install
```

## Ejecutar tareas comunes

Con just puedes ejecutar tareas habituales del proyecto:

- Iniciar el servidor MCP:
  ```bash
  just run
  ```
- Ejecutar los tests:
  ```bash
  just test
  ```

Alternativamente, puedes usar Poetry directamente:

- Iniciar el servidor:
  ```bash
  poetry run readium-mcp
  ```
- Ejecutar los tests:
  ```bash
  poetry run pytest
  ```

## Ejecutar el servidor FastMCP

El servidor MCP ahora se ejecuta como una aplicación ASGI usando Starlette y uvicorn, y se expone en el puerto **8000**.

Lanza el servidor con el siguiente comando:

```bash
poetry run readium-mcp
```

Esto iniciará el servidor en:  
http://localhost:8000

Esto inicia un servidor MCP que expone la herramienta principal:

- **analyze_docs** — Analiza documentación desde un directorio local, repositorio Git o URL usando Readium. Devuelve un resumen, un árbol de la estructura y el contenido.

### Parámetros de `analyze_docs`

- `path` (str, requerido): Ruta local, URL de repo GitHub o URL de documentación.
- `branch` (str, opcional): Rama a usar si es un repo.
- `target_dir` (str, opcional): Subdirectorio a analizar.
- `use_markitdown` (bool): Usa Markitdown para Markdown (por defecto: False).
- `url_mode` (str): Modo de URL ('clean', 'raw', etc.; por defecto: 'clean').
- `max_file_size` (int): Tamaño máximo de archivo en bytes (por defecto: 5MB).
- `exclude_dirs` (list[str]): Directorios a excluir.
- `exclude_ext` (list[str]): Extensiones a excluir (ej: ['.png']).
- `include_ext` (list[str]): Extensiones a incluir (ej: ['.md']).

### Ejemplo de uso

Puedes probar la herramienta usando clientes MCP compatibles, como la CLI `mcp` o integraciones en Claude Desktop.

El resultado es un diccionario con:
- `content`: lista de bloques de texto (`summary`, `tree`, `content`)
- `isError`: booleano, indica si hubo error

## Ejecutar los tests

Para ejecutar los tests unitarios con Poetry:

```bash
poetry run pytest
```

O usando just:

```bash
just test
```

Esto buscará y ejecutará todos los tests en el directorio `tests/`.
