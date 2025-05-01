import sys
from pathlib import Path
# Add parent directory to sys.path to enable imports from src
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import types
from unittest.mock import AsyncMock, MagicMock, patch

import src.server as server

@pytest.fixture
def mock_readium(monkeypatch):
    mock_config = MagicMock(name="ReadConfig")
    mock_reader = MagicMock(name="Readium")
    monkeypatch.setattr(server, "ReadConfig", MagicMock(return_value=mock_config))
    monkeypatch.setattr(server, "Readium", MagicMock(return_value=mock_reader))
    return mock_config, mock_reader

@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.report_progress = AsyncMock()
    ctx.error = AsyncMock()
    return ctx

@pytest.mark.asyncio
async def test_analyze_docs_success(mock_readium, mock_ctx):
    mock_config, mock_reader = mock_readium
    # Simulate read_docs returning summary, tree, content
    mock_reader.read_docs.return_value = ("summary", "tree", "content")
    result = await server.analyze_docs(
        path="docs/",
        branch="main",
        target_dir="target/",
        use_markitdown=True,
        url_mode="clean",
        max_file_size=1234,
        exclude_dirs=[".git"],
        exclude_ext=[".log"],
        include_ext=[".md"],
        ctx=mock_ctx,
    )
    assert result["isError"] is False
    assert isinstance(result["content"], list)
    assert "Summary:" in result["content"][0]["text"]
    assert "Tree:" in result["content"][1]["text"]
    assert "Content:" in result["content"][2]["text"]
    mock_reader.read_docs.assert_called_once_with("docs/", branch="main")
    mock_ctx.info.assert_any_await("Analyzing documentation from: docs/")
    mock_ctx.report_progress.assert_any_await(0, 100)
    mock_ctx.info.assert_any_await("Analysis completed")
    mock_ctx.report_progress.assert_any_await(100, 100)

@pytest.mark.asyncio
async def test_analyze_docs_optional_params(mock_readium, mock_ctx):
    mock_config, mock_reader = mock_readium
    mock_reader.read_docs.return_value = ("sum", "tree", "cont")
    # Call with only required param
    result = await server.analyze_docs(path="docs/", ctx=mock_ctx)
    assert result["isError"] is False
    mock_reader.read_docs.assert_called_once_with("docs/", branch=None)

@pytest.mark.asyncio
async def test_analyze_docs_error_handling(mock_readium, mock_ctx):
    mock_config, mock_reader = mock_readium
    mock_reader.read_docs.side_effect = Exception("fail!")
    result = await server.analyze_docs(path="docs/", ctx=mock_ctx)
    assert result["isError"] is True
    assert "fail!" in result["content"][0]["text"]
    mock_ctx.error.assert_awaited_with("Error analyzing documentation: fail!")

@pytest.mark.asyncio
async def test_analyze_docs_no_ctx(mock_readium):
    mock_config, mock_reader = mock_readium
    mock_reader.read_docs.return_value = ("s", "t", "c")
    # ctx is None: should not raise
    result = await server.analyze_docs(path="docs/")
    assert result["isError"] is False
    assert "Summary:" in result["content"][0]["text"]

def test_main_runs_server(monkeypatch):
    # Patch mcp.run and logger
    run_mock = MagicMock()
    monkeypatch.setattr(server.mcp, "run", run_mock)
    logger_mock = MagicMock()
    monkeypatch.setattr(server, "logger", logger_mock)
    # Patch sys.stderr to avoid print output
    monkeypatch.setattr(sys, "stderr", MagicMock())
    server.main()
    run_mock.assert_called_once_with(transport="stdio")
