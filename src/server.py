#!/usr/bin/env python3
import logging
import sys
from mcp.server.fastmcp import FastMCP, Context
from readium import Readium, ReadConfig
from typing import Optional, List, Dict, Any
import traceback
import asyncio

# Configure logging to stderr, DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("readium-mcp")

logger.debug("Importing modules and initializing server...")

# Create the MCP server with properly structured capabilities
# IMPORTANT: Pass capabilities as a dictionary to the constructor
mcp = FastMCP("Readium MCP Server")

logger.info("MCP server instance created.")

@mcp.tool(
    description=(
        "Analyze documentation from a local directory, Git repo, or URL using Readium. "
        "Returns a summary, tree structure, and content."
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
    Analyze documentation using Readium and return structured results.
    """
    logger.info("Received analyze_docs request.")
    logger.debug(f"Parameters: path={path}, branch={branch}, target_dir={target_dir}, "
                 f"use_markitdown={use_markitdown}, url_mode={url_mode}, "
                 f"max_file_size={max_file_size}, exclude_dirs={exclude_dirs}, "
                 f"exclude_ext={exclude_ext}, include_ext={include_ext}")

    try:
        # Report progress if context is available
        if ctx:
            ctx.info(f"Analyzing documentation from: {path}")
            await ctx.report_progress(0, 100)
        logger.info(f"Analyzing documentation from: {path}")

        # Configure Readium
        config_kwargs = {
            "max_file_size": max_file_size,
            "target_dir": target_dir,
            "use_markitdown": use_markitdown,
            "url_mode": url_mode,
            "debug": True,
        }

        # Add optional configuration
        if exclude_dirs is not None:
            config_kwargs["exclude_dirs"] = set(exclude_dirs)
        if exclude_ext is not None:
            config_kwargs["exclude_extensions"] = set(exclude_ext)
        if include_ext is not None:
            config_kwargs["include_extensions"] = set(include_ext)

        logger.debug(f"ReadConfig kwargs: {config_kwargs}")

        # Create Readium instance
        config = ReadConfig(**config_kwargs)
        reader = Readium(config)

        # Progress update
        if ctx:
            ctx.info("Starting analysis...")
            await ctx.report_progress(30, 100)
        logger.info("Starting Readium analysis...")

        # Process documentation
        logger.debug("Calling reader.read_docs()...")
        summary, tree, content = reader.read_docs(path, branch=branch)
        logger.debug("Readium analysis complete.")

        # Final progress update
        if ctx:
            ctx.info("Analysis completed")
            await ctx.report_progress(100, 100)
        logger.info("Analysis completed successfully.")

        # Return formatted results
        return {
            "content": [
                {"type": "text", "text": f"Summary:\n{summary}"},
                {"type": "text", "text": f"Tree:\n{tree}"},
                {"type": "text", "text": f"Content:\n{content}"},
            ],
            "isError": False,
        }
    except Exception as e:
        # Handle errors
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        logger.error(f"Exception in analyze_docs: {error_message}")

        if ctx:
            ctx.error(f"Error analyzing documentation: {str(e)}")

        return {
            "content": [{"type": "text", "text": error_message}],
            "isError": True,
        }

def main():
    """Run the MCP server"""
    logger.info("Starting Readium MCP Server (stdio transport)...")
    print("Starting Readium MCP Server...", file=sys.stderr)
    # Run the server using stdio transport by default
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    main()