"""
Tests for MCP server tool calling logic.

Tests the MCPDesignSystemServer.call_tool method and internal handlers
for get_design_system, get_aesthetic_guidance, unknown tools, and
error conditions.
"""
import json
import unittest
from unittest.mock import patch, MagicMock

from .server import MCPDesignSystemServer, MCPToolResponse


class TestMCPCallTool(unittest.TestCase):
    """Tests for MCPDesignSystemServer.call_tool and get_tools."""

    def _create_mock_design_system(
        self,
        name="Test Vibe",
        description="A vibrant design",
        tokens=None,
        aesthetic="",
    ):
        """Create a mock design system for testing."""
        mock_ds = MagicMock()
        mock_ds.id = "test-uuid-123"
        mock_ds.name = name
        mock_ds.description = description
        mock_ds.design_tokens = tokens or {
            "colors": {"primary": "#FF0000", "secondary": "#00FF00"},
            "typography": {"fontFamily": "Inter", "fontWeight": "400,700"},
            "shadowDepth": 3,
        }
        mock_ds.aesthetic_analysis = aesthetic
        mock_ds.user_id = "user-uuid-456"
        return mock_ds

    @patch("apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system")
    def test_call_get_design_system(self, mock_load):
        """call_tool('get_design_system') returns design system data."""
        mock_ds = self._create_mock_design_system()
        mock_load.return_value = mock_ds

        server = MCPDesignSystemServer("test-uuid-123", "test-key")
        response = server.call_tool("get_design_system", {})

        self.assertIsInstance(response, MCPToolResponse)
        self.assertFalse(response.is_error)
        self.assertEqual(len(response.content), 1)
        self.assertEqual(response.content[0]["type"], "text")

        data = json.loads(response.content[0]["text"])
        self.assertEqual(data["name"], "Test Vibe")
        self.assertEqual(data["description"], "A vibrant design")
        self.assertIn("colors", data)
        self.assertEqual(data["colors"]["primary"], "#FF0000")
        self.assertIn("typography", data)
        self.assertEqual(data["shadowDepth"], 3)

    @patch("apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system")
    def test_call_get_aesthetic_guidance_with_analysis(self, mock_load):
        """call_tool('get_aesthetic_guidance') returns aesthetic analysis text."""
        mock_ds = self._create_mock_design_system(
            aesthetic="# Soul Invariants\n- Warm and inviting\n"
        )
        mock_load.return_value = mock_ds

        server = MCPDesignSystemServer("test-uuid-123", "test-key")
        response = server.call_tool("get_aesthetic_guidance", {})

        self.assertIsInstance(response, MCPToolResponse)
        self.assertFalse(response.is_error)
        text = response.content[0]["text"]
        self.assertIn("Soul Invariants", text)
        self.assertIn("Warm and inviting", text)

    @patch("apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system")
    def test_call_get_aesthetic_guidance_empty(self, mock_load):
        """call_tool('get_aesthetic_guidance') with no analysis returns message."""
        mock_ds = self._create_mock_design_system(aesthetic="")
        mock_load.return_value = mock_ds

        server = MCPDesignSystemServer("test-uuid-123", "test-key")
        response = server.call_tool("get_aesthetic_guidance", {})

        self.assertFalse(response.is_error)
        text = response.content[0]["text"]
        self.assertIn("No aesthetic analysis available", text)

    @patch("apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system")
    def test_call_unknown_tool(self, mock_load):
        """call_tool('unknown_tool') returns error MCPToolResponse."""
        mock_load.return_value = self._create_mock_design_system()

        server = MCPDesignSystemServer("test-uuid-123", "test-key")
        response = server.call_tool("unknown_tool", {})

        self.assertIsInstance(response, MCPToolResponse)
        self.assertTrue(response.is_error)
        self.assertIn("Unknown tool", response.content[0]["text"])

    @patch("apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system")
    def test_call_tool_design_system_not_found(self, mock_load):
        """call_tool when design system not found returns error."""
        mock_load.return_value = None

        server = MCPDesignSystemServer("nonexistent-uuid", "test-key")
        response = server.call_tool("get_design_system", {})

        self.assertIsInstance(response, MCPToolResponse)
        self.assertTrue(response.is_error)
        self.assertIn("not found", response.content[0]["text"])

    @patch("apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system")
    def test_get_tools_design_system_not_found(self, mock_load):
        """get_tools when design system not found returns empty list."""
        mock_load.return_value = None

        server = MCPDesignSystemServer("nonexistent-uuid", "test-key")
        tools = server.get_tools()

        self.assertEqual(tools, [])


if __name__ == "__main__":
    unittest.main()
