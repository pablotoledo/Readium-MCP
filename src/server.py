from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, List, Dict, Any
import traceback
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from readium import Readium, ReadConfig

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Definir lifespan para inicialización temprana
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """
    Inicializa recursos críticos antes de aceptar peticiones.
    """
    print("Iniciando servidor MCP, preparando recursos...")
    try:
        # Aquí puedes poner inicialización real (conexiones, modelos, etc.)
        await asyncio.sleep(1)  # Simulación de inicialización rápida
        print("Servidor completamente inicializado y listo para peticiones")
        yield None
    finally:
        print("Cerrando servidor MCP...")

# Crear el servidor con lifespan y dependencias explícitas
# IMPORTANTE: Configurar las capacidades para permitir listar herramientas
mcp = FastMCP(
    "Readium MCP Server", 
    lifespan=app_lifespan,
    dependencies=["readium", "mcp"],  # Declara las dependencias
    capabilities={
        "tools": {
            "listChanged": True  # Habilitar listado de herramientas
        },
        "resources": {
            "subscribe": True,
            "listChanged": True
        },
        "prompts": {
            "listChanged": True
        }
    }
)

@mcp.tool(
    description=(
        "Analyze documentation from a local directory, Git repo, or URL using Readium. "
        "Returns a summary, a tree of the doc structure, and the content. "
        "Arguments: path (str, required), branch (str, optional), target_dir (str, optional), "
        "use_markitdown (bool), url_mode (str), max_file_size (int), "
        "exclude_dirs/include_ext/exclude_ext (list of str). "
        "Output: dict with 'content' (summary, tree, content) and 'isError' (bool)."
    )
)
async def analyze_docs(
    path: str,
    branch: Optional[str] = None,
    target_dir: Optional[str] = None,
    use_markitdown: bool = False,
    url_mode: str = "clean",
    max_file_size: int = 5 * 1024 * 1024,
    exclude_dirs: Optional[List[str]] = None,
    exclude_ext: Optional[List[str]] = None,
    include_ext: Optional[List[str]] = None,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Analyze documentation using Readium and return summary, tree, and content.
    """
    try:
        # Si ctx está disponible, usarlo para reportar progreso
        if ctx:
            ctx.info(f"Analyzing documentation from: {path}")
            await ctx.report_progress(0, 100)
        
        config_kwargs = {
            "max_file_size": max_file_size,
            "target_dir": target_dir,
            "use_markitdown": use_markitdown,
            "url_mode": url_mode,
            "debug": True,  # Habilitar debug para más información
        }
        if exclude_dirs is not None:
            config_kwargs["exclude_dirs"] = set(exclude_dirs)
        if exclude_ext is not None:
            config_kwargs["exclude_extensions"] = set(exclude_ext)
        if include_ext is not None:
            config_kwargs["include_extensions"] = set(include_ext)
        
        config = ReadConfig(**config_kwargs)
        reader = Readium(config)
        
        # Reportar progreso intermedio
        if ctx:
            ctx.info("Readium configurado, iniciando análisis...")
            await ctx.report_progress(30, 100)
        
        summary, tree, content = reader.read_docs(path, branch=branch)
        
        # Reportar finalización
        if ctx:
            ctx.info("Análisis completado")
            await ctx.report_progress(100, 100)
        
        return {
            "content": [
                {"type": "text", "text": f"Summary:\n{summary}"},
                {"type": "text", "text": f"Tree:\n{tree}"},
                {"type": "text", "text": f"Content:\n{content}"},
            ],
            "isError": False,
        }
    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"Error: {str(e)}\n{tb}"
        
        # Reportar error si hay contexto
        if ctx:
            ctx.error(f"Error en analyze_docs: {str(e)}")
        
        return {
            "content": [
                {"type": "text", "text": error_message}
            ],
            "isError": True,
        }

def main():
    try:
        print("Starting the Readium MCP server on http://localhost:8000 ...")
        logging.basicConfig(level=logging.DEBUG)

        # Endpoint de health para verificar que el servidor está funcionando
        async def health(request):
            return JSONResponse({"status": "healthy", "server": "readium-mcp"})

        # Configurar middleware CORS para permitir conexiones
        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]

        # Crear instancia de la aplicación MCP
        # NOTA: Esta aplicación maneja tanto SSE como mensajes JSON-RPC
        mcp_app = mcp.sse_app()

        # Montar el servidor MCP correctamente
        app = Starlette(
            routes=[
                Route("/health", health),
                # El endpoint principal que maneja tanto SSE como mensajes
                Mount("/", app=mcp_app),
            ],
            middleware=middleware,
        )
        
        print("Servidor MCP configurado correctamente")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="debug",
            timeout_keep_alive=120
        )
    except Exception as e:
        print(f"Error initializing server: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()