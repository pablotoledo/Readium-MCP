from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from src.server import analyze_docs

# Adaptamos los tests para una función async
@pytest.mark.asyncio
@patch("src.server.Readium")
@patch("src.server.ReadConfig")
async def test_analyze_docs_success(MockReadConfig, MockReadium):
    # Mock Readium instance and its read_docs method
    mock_reader = MagicMock()
    mock_reader.read_docs.return_value = ("Resumen", "Árbol", "Contenido")
    MockReadium.return_value = mock_reader

    # Call analyze_docs with minimal required args
    result = await analyze_docs("some/path")
    assert not result["isError"]
    assert result["content"][0]["text"] == "Summary:\nResumen"
    assert result["content"][1]["text"] == "Tree:\nÁrbol"
    assert result["content"][2]["text"] == "Content:\nContenido"

@pytest.mark.asyncio
@patch("src.server.Readium")
@patch("src.server.ReadConfig")
async def test_analyze_docs_exception(MockReadConfig, MockReadium):
    # Simulate exception in read_docs
    mock_reader = MagicMock()
    mock_reader.read_docs.side_effect = Exception("fail!")
    MockReadium.return_value = mock_reader

    result = await analyze_docs("bad/path")
    assert result["isError"]
    assert "fail!" in result["content"][0]["text"]

# Nuevo test para verificar Context
@pytest.mark.asyncio
@patch("src.server.Readium")
@patch("src.server.ReadConfig")
async def test_analyze_docs_with_context(MockReadConfig, MockReadium):
    # Mock Readium instance and its read_docs method
    mock_reader = MagicMock()
    mock_reader.read_docs.return_value = ("Resumen", "Árbol", "Contenido")
    MockReadium.return_value = mock_reader
    
    # Mock Context con métodos asíncronos
    mock_context = MagicMock()
    mock_context.info = MagicMock()
    mock_context.report_progress = AsyncMock()
    mock_context.error = MagicMock()
    
    # Call analyze_docs with context
    result = await analyze_docs("some/path", ctx=mock_context)
    
    # Verify context methods were called
    mock_context.info.assert_called()
    mock_context.report_progress.assert_called()
    assert not result["isError"]
