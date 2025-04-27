import unittest
from unittest.mock import patch, MagicMock
from src.server import analyze_docs

class TestAnalyzeDocs(unittest.TestCase):
    @patch("src.server.Readium")
    @patch("src.server.ReadConfig")
    def test_analyze_docs_success(self, MockReadConfig, MockReadium):
        # Mock Readium instance and its read_docs method
        mock_reader = MagicMock()
        mock_reader.read_docs.return_value = ("Resumen", "Árbol", "Contenido")
        MockReadium.return_value = mock_reader

        # Call analyze_docs with minimal required args
        result = analyze_docs("some/path")
        self.assertFalse(result["isError"])
        self.assertEqual(result["content"][0]["text"], "Summary:\nResumen")
        self.assertEqual(result["content"][1]["text"], "Tree:\nÁrbol")
        self.assertEqual(result["content"][2]["text"], "Content:\nContenido")

    @patch("src.server.Readium")
    @patch("src.server.ReadConfig")
    def test_analyze_docs_exception(self, MockReadConfig, MockReadium):
        # Simulate exception in read_docs
        mock_reader = MagicMock()
        mock_reader.read_docs.side_effect = Exception("fail!")
        MockReadium.return_value = mock_reader

        result = analyze_docs("bad/path")
        self.assertTrue(result["isError"])
        self.assertIn("fail!", result["content"][0]["text"])

if __name__ == "__main__":
    unittest.main()
