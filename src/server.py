from mcp.server.fastmcp import FastMCP
from typing import Optional, List
import traceback

from readium import Readium, ReadConfig

mcp = FastMCP("Readium MCP Server")

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
def analyze_docs(
    path: str,
    branch: Optional[str] = None,
    target_dir: Optional[str] = None,
    use_markitdown: bool = False,
    url_mode: str = "clean",
    max_file_size: int = 5 * 1024 * 1024,
    exclude_dirs: Optional[List[str]] = None,
    exclude_ext: Optional[List[str]] = None,
    include_ext: Optional[List[str]] = None,
) -> dict:
    """
    Analyze documentation using Readium and return summary, tree, and content.
    """
    try:
        # Build config_kwargs with only the parameters that have values
        config_kwargs = {
            "max_file_size": max_file_size,
            "target_dir": target_dir,
            "use_markitdown": use_markitdown,
            "url_mode": url_mode,
        }
        
        # Only add these parameters if they aren't None
        if exclude_dirs is not None:
            config_kwargs["exclude_dirs"] = set(exclude_dirs)
        if exclude_ext is not None:
            config_kwargs["exclude_extensions"] = set(exclude_ext)
        if include_ext is not None:
            config_kwargs["include_extensions"] = set(include_ext)
            
        config = ReadConfig(**config_kwargs)
        reader = Readium(config)
        summary, tree, content = reader.read_docs(path, branch=branch)
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
        return {
            "content": [
                {"type": "text", "text": f"Error: {str(e)}\n{tb}"}
            ],
            "isError": True,
        }
    
def main():
    print("Starting the Readium MCP server on http://localhost:8000 ...")
    from starlette.applications import Starlette
    from starlette.routing import Mount
    import uvicorn

    app = Starlette(
        routes=[
            Mount("/", app=mcp.sse_app()),
        ]
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
