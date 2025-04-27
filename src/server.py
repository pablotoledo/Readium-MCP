from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Readium MCP Hello World")

print("Starting the FastMCP server...")

@mcp.resource("hello://world")
def hello_world() -> str:
    """Returns a Hello World greeting."""
    return "Hello World from FastMCP!"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
