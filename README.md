# Readium MCP

This project provides a minimal [FastMCP](https://modelcontextprotocol.io) server that exposes Readium's documentation analysis functionality via the MCP protocol.

## Requirements

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/)

## Installation

Install dependencies with Poetry:

```bash
poetry install
```

## Running the MCP Server

Start the server using Poetry:

```bash
poetry run readium-mcp
```

This will launch the MCP server using stdio transport (no HTTP, no Starlette, no uvicorn).

## Usage

You can use this server with any MCP-compatible client, such as the [MCP CLI](https://github.com/modelcontextprotocol/cli) or Claude Desktop.

### MCP CLI Example

Install the MCP CLI and register the server:

```bash
mcp install -n readium-mcp -- poetry run readium-mcp
mcp inspect readium-mcp
```

### Claude Desktop Example

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "readium": {
      "command": "poetry",
      "args": ["run", "readium-mcp"]
    }
  }
}
```

## Exposed Tool

- **analyze_docs** — Analyze documentation from a local directory, Git repo, or URL using Readium. Returns a summary, tree structure, and content.

#### Parameters

- `path` (str, required): Local path, GitHub repo URL, or documentation URL.
- `branch` (str, optional): Branch to use if a repo.
- `target_dir` (str, optional): Subdirectory to analyze.
- `use_markitdown` (bool): Use Markitdown for Markdown (default: False).
- `url_mode` (str): URL mode ('clean', 'raw', etc.; default: 'clean').
- `max_file_size` (int): Max file size in bytes (default: 5MB).
- `exclude_dirs` (list[str]): Directories to exclude.
- `exclude_ext` (list[str]): Extensions to exclude (e.g., ['.png']).
- `include_ext` (list[str]): Extensions to include (e.g., ['.md']).

#### Output

Returns a dictionary with:
- `content`: list of text blocks (`summary`, `tree`, `content`)
- `isError`: boolean, indicates if there was an error

## Testing

To run unit tests:

```bash
poetry run pytest
```

---

This minimal setup avoids HTTP servers and focuses on stdio-based MCP communication for maximum compatibility and simplicity.
