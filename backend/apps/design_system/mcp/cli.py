#!/usr/bin/env python
"""
MonkeyUI MCP Server - stdio transport entry point.

This script provides the CLI entry point for running the MCP server
with stdio transport, which is used by tools like Cursor and Claude Desktop.

Usage:
    python -m apps.design_system.mcp.cli --design-system-id <uuid> --api-key <key>
    
Or via the installed command:
    monkeyui-mcp --design-system-id <uuid> --api-key <key>
"""
import os
import sys
import asyncio
import argparse


def main():
    """Main entry point for the MCP CLI."""
    parser = argparse.ArgumentParser(
        description="MonkeyUI MCP Server - Expose design systems to AI coding assistants"
    )
    parser.add_argument(
        "--design-system-id",
        required=True,
        help="UUID of the design system to expose"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="API key for authentication"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Setup Django before importing models
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Add the backend directory to path if not already there
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    import django
    django.setup()
    
    # Configure logging
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Import and run the server
    from apps.design_system.mcp.mcp_server import run_stdio_server
    
    # FastMCP's run() handles its own event loop, no asyncio.run needed
    run_stdio_server(args.design_system_id, args.api_key)


if __name__ == "__main__":
    main()
