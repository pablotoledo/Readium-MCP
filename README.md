# Readium MCP

<p align="center">
  <img src="https://raw.githubusercontent.com/pablotoledo/readium/main/logo.webp" alt="Readium MCP" width="200">
</p>

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-compatible-green)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/readium-mcp.svg)](https://pypi.org/project/readium-mcp/)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that exposes the powerful documentation analysis functionality of [Readium](https://github.com/pablotoledo/readium) for LLMs like Claude and other MCP-compatible clients.

## 🔍 What is this?

Readium MCP acts as a bridge between LLMs and any documentation repository, allowing:

- Analyzing local directories, public/private Git repositories, and URLs
- Processing multiple file formats (code, Markdown, text)
- Converting web pages to Markdown for analysis
- Delivering structured results with summary, file tree, and content

Perfect for when you need an LLM to analyze large bodies of documentation, code repositories, or technical websites.

## 🚀 Installation

### With pip (recommended)

```bash
pip install readium-mcp
```

### From source code

```bash
# Clone the repository
git clone https://github.com/tu-usuario/readium-mcp.git
cd readium-mcp

# Install dependencies with Poetry
poetry install
```

## 🛠️ Usage

### Direct execution

```bash
readium-mcp
```

### With Poetry (from source code)

```bash
poetry run readium-mcp
```

## 🔌 Integration with MCP clients

### VSCode

Add to your VSCode configuration (settings.json):

```json
{
  "mcp": {
    "servers": {
      "readium": {
        "command": "readium-mcp"
      }
    }
  }
}
```

Or create a `.vscode/mcp.json` file in your project:

```json
{
  "servers": {
    "readium": {
      "command": "readium-mcp"
    }
  }
}
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "readium": {
      "command": "readium-mcp"
    }
  }
}
```

### MCP CLI

```bash
# Install
mcp install -n readium -- readium-mcp

# Inspect
mcp inspect readium

# Test in console
mcp call-tool readium analyze_docs --path https://github.com/modelcontextprotocol/servers.git
```

## 📝 Exposed tools

### analyze_docs

Analyzes documentation from a local directory, Git repository, or URL using Readium.

#### Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `path` | string | Local path, GitHub URL, or documentation URL | (required) |
| `branch` | string | Branch to use if it's a repository | `null` |
| `target_dir` | string | Specific subdirectory to analyze | `null` |
| `use_markitdown` | boolean | Use Markitdown for conversion | `false` |
| `url_mode` | string | URL processing mode ('clean', 'full') | `"clean"` |
| `max_file_size` | integer | Maximum file size in bytes | `5242880` (5MB) |
| `exclude_dirs` | array | Directories to exclude | `[]` |
| `exclude_ext` | array | Extensions to exclude (e.g., ['.png']) | `[]` |
| `include_ext` | array | Extensions to include (e.g., ['.md']) | `[]` |

#### Response

```json
{
  "content": [
    {"type": "text", "text": "Summary:\n..."},
    {"type": "text", "text": "Tree:\n..."},
    {"type": "text", "text": "Content:\n..."}
  ],
  "isError": false
}
```

## 🧪 Testing

### Unit tests

```bash
poetry run pytest
```

### Direct Readium test

```bash
python test.py
```

## 🧩 Example usage with Python

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_readium_mcp():
    server_params = StdioServerParameters(
        command="readium-mcp"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # Analyze a repository
            result = await session.call_tool(
                "analyze_docs",
                {"path": "https://github.com/modelcontextprotocol/servers.git"}
            )

            print(f"Analysis result: {result}")

# Run
asyncio.run(test_readium_mcp())
```

## 📋 Advantages

- **Fast**: Efficient analysis even for large repositories
- **Flexible**: Works with local directories, Git repositories, and URLs
- **Configurable**: Customize extensions, sizes, and directories to analyze
- **Compatible**: Works with any MCP client (Claude, VSCode, CLI)
- **Simple**: No complex dependencies, stdio transport for maximum compatibility

## 🤝 Contributing

Contributions are welcome. Please feel free to:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- [Readium](https://github.com/pablotoledo/readium) for the powerful documentation analysis functionality
- [Model Context Protocol](https://modelcontextprotocol.io) for the standard LLM communication protocol
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for the Python SDK for MCP

---

Developed with ❤️ by Pablo Toledo
