# Readium MCP

Este proyecto incluye un servidor [FastMCP](https://modelcontextprotocol.io) de ejemplo integrado con Poetry.

## Requisitos

- Python 3.10 o superior
- [Poetry](https://python-poetry.org/)

## Instalación de dependencias

```bash
poetry install
```

## Ejecutar el servidor FastMCP (Hola Mundo)

Lanza el servidor MCP con el siguiente comando:

```bash
poetry run python src/readium_mcp/server.py
```

Esto inicia un servidor MCP que expone el recurso:

- **hello://world** — Devuelve el mensaje: `¡Hola Mundo desde FastMCP!`

Puedes probarlo usando herramientas compatibles con MCP, como la CLI `mcp` o integrándolo en Claude Desktop.
