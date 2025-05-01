#!/usr/bin/env python3
"""
Direct test of Readium MCP functionality without spawning a subprocess
"""

import sys

from readium import ReadConfig, Readium


# Test basic Readium functionality
def test_readium_direct():
    print("Testing Readium directly...")

    # Configure Readium
    config = ReadConfig(debug=True)
    reader = Readium(config)

    # Test with a small public repository
    test_repo = "https://github.com/modelcontextprotocol/servers.git"
    print(f"Analyzing repository: {test_repo}")

    try:
        summary, tree, content = reader.read_docs(test_repo)

        print("\nAnalysis result:")
        print(f"\n--- Summary ---\n{summary[:500]}...")
        print(f"\n--- Tree ---\n{tree[:500]}...")
        print(f"\n--- Content (first 500 chars) ---\n{content[:500]}...")

        return True
    except Exception as e:
        print(f"Error analyzing repository: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = test_readium_direct()
    sys.exit(0 if success else 1)
