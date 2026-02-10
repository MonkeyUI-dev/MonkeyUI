"""
Tests for MCP server annotations and tool definitions.

These tests verify that MCP tools include proper annotations per the
2025-06-18 specification and that priority hints are correctly set
to resolve conflicts with third-party design tools.
"""
import unittest
from unittest.mock import patch, MagicMock

from .server import MCPDesignSystemServer, MCPTool, MCPToolAnnotations


class TestMCPToolAnnotations(unittest.TestCase):
    """Test MCPToolAnnotations dataclass."""

    def test_to_dict_full(self):
        """All fields should be serialized when set."""
        annotations = MCPToolAnnotations(
            title="Test Tool",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        )
        result = annotations.to_dict()
        self.assertEqual(result, {
            "title": "Test Tool",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        })

    def test_to_dict_omits_none(self):
        """None values should be omitted from serialization."""
        annotations = MCPToolAnnotations(
            title="Partial",
            readOnlyHint=True,
        )
        result = annotations.to_dict()
        self.assertEqual(result, {
            "title": "Partial",
            "readOnlyHint": True,
        })
        self.assertNotIn("destructiveHint", result)
        self.assertNotIn("idempotentHint", result)
        self.assertNotIn("openWorldHint", result)

    def test_to_dict_empty(self):
        """Default annotations should produce an empty dict."""
        annotations = MCPToolAnnotations()
        result = annotations.to_dict()
        self.assertEqual(result, {})


class TestMCPTool(unittest.TestCase):
    """Test MCPTool dataclass."""

    def test_tool_with_annotations(self):
        """Tool should accept annotations."""
        annotations = MCPToolAnnotations(
            title="My Tool",
            readOnlyHint=True,
        )
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            annotations=annotations,
        )
        self.assertEqual(tool.annotations.title, "My Tool")
        self.assertTrue(tool.annotations.readOnlyHint)

    def test_tool_without_annotations(self):
        """Tool should work without annotations (backward compatible)."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
        )
        self.assertIsNone(tool.annotations)


class TestMCPDesignSystemServerTools(unittest.TestCase):
    """Test that MCP tools have correct annotations and priority descriptions."""

    def _create_mock_design_system(self, name="Test Design"):
        """Create a mock design system for testing."""
        mock_ds = MagicMock()
        mock_ds.id = "test-uuid"
        mock_ds.name = name
        mock_ds.description = "A test design system"
        mock_ds.design_tokens = {"colors": {}, "typography": {}}
        mock_ds.aesthetic_analysis = "# Test aesthetic"
        mock_ds.user_id = "user-123"
        return mock_ds

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_tools_have_annotations(self, mock_load):
        """All tools should have annotations."""
        mock_load.return_value = self._create_mock_design_system()
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()

        for tool in tools:
            self.assertIsNotNone(tool.annotations, f"Tool '{tool.name}' missing annotations")

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_tools_are_read_only(self, mock_load):
        """All tools should be marked as read-only."""
        mock_load.return_value = self._create_mock_design_system()
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()

        for tool in tools:
            self.assertTrue(tool.annotations.readOnlyHint, f"Tool '{tool.name}' should be read-only")
            self.assertFalse(tool.annotations.destructiveHint, f"Tool '{tool.name}' should not be destructive")
            self.assertTrue(tool.annotations.idempotentHint, f"Tool '{tool.name}' should be idempotent")
            self.assertFalse(tool.annotations.openWorldHint, f"Tool '{tool.name}' should be closed-world")

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_tools_have_titles(self, mock_load):
        """All tools should have human-readable titles."""
        mock_load.return_value = self._create_mock_design_system("My Brand")
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()

        for tool in tools:
            self.assertIsNotNone(tool.annotations.title, f"Tool '{tool.name}' missing title")
            self.assertIn("My Brand", tool.annotations.title)

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_tool_descriptions_assert_priority(self, mock_load):
        """Tool descriptions should assert authoritative priority."""
        mock_load.return_value = self._create_mock_design_system()
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()

        for tool in tools:
            desc = tool.description.upper()
            self.assertIn("AUTHORITATIVE", desc, f"Tool '{tool.name}' missing AUTHORITATIVE in description")
            self.assertIn("HIGHEST PRIORITY", desc, f"Tool '{tool.name}' missing HIGHEST PRIORITY in description")
            self.assertIn("MUST TAKE PRECEDENCE", desc, f"Tool '{tool.name}' missing MUST TAKE PRECEDENCE in description")

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_annotations_serialization_in_tool_list(self, mock_load):
        """Annotations should serialize correctly for JSON-RPC responses."""
        mock_load.return_value = self._create_mock_design_system("Test")
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()

        for tool in tools:
            serialized = tool.annotations.to_dict()
            self.assertIn("title", serialized)
            self.assertIn("readOnlyHint", serialized)
            self.assertIn("destructiveHint", serialized)
            self.assertIn("idempotentHint", serialized)
            self.assertIn("openWorldHint", serialized)

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_input_schema_no_params_format(self, mock_load):
        """No-parameter tools should use recommended 2025-11-25 inputSchema format."""
        mock_load.return_value = self._create_mock_design_system()
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()

        for tool in tools:
            schema = tool.input_schema
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema.get("additionalProperties", True),
                             f"Tool '{tool.name}' should use additionalProperties: false")
            self.assertNotIn("properties", schema,
                             f"Tool '{tool.name}' should omit empty properties per 2025-11-25 spec")

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_get_design_system_tool_present(self, mock_load):
        """get_design_system tool should be in tool list."""
        mock_load.return_value = self._create_mock_design_system()
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()
        tool_names = [t.name for t in tools]
        self.assertIn("get_design_system", tool_names)

    @patch('apps.design_system.mcp.server.MCPDesignSystemServer._load_design_system')
    def test_get_aesthetic_guidance_tool_present(self, mock_load):
        """get_aesthetic_guidance tool should be in tool list."""
        mock_load.return_value = self._create_mock_design_system()
        server = MCPDesignSystemServer("test-uuid", "test-key")
        tools = server.get_tools()
        tool_names = [t.name for t in tools]
        self.assertIn("get_aesthetic_guidance", tool_names)


if __name__ == '__main__':
    unittest.main()
