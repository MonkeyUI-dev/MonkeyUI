"""
MCP API views for exposing design systems to vibe coding tools.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .server import MCPDesignSystemServer, get_design_system_mcp_config


def get_api_key_from_request(request) -> str:
    """Extract API key from request headers."""
    # Support multiple header formats
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Also support X-API-Key header
    return request.headers.get('X-API-Key', '')


@extend_schema(
    responses={
        200: OpenApiResponse(description="List of available MCP tools"),
        401: OpenApiResponse(description="Invalid or missing API key"),
        404: OpenApiResponse(description="Design system not found or MCP not enabled"),
    },
    description="Get available MCP tools for a design system",
    tags=["MCP"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def mcp_list_tools(request, design_system_id: str):
    """
    List available MCP tools for a design system.
    
    This endpoint returns the tools that vibe coding assistants
    can use to access design system data.
    """
    api_key = get_api_key_from_request(request)
    
    server = MCPDesignSystemServer(design_system_id, api_key)
    
    if not server.validate_api_key(api_key):
        return Response(
            {"error": _("Invalid or missing API key")},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tools = server.get_tools()
    
    if not tools:
        return Response(
            {"error": _("Design system not found or MCP not enabled")},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response({
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in tools
        ]
    })


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Tool name to call"},
                "arguments": {"type": "object", "description": "Tool arguments"}
            },
            "required": ["name"]
        }
    },
    responses={
        200: OpenApiResponse(description="Tool call result"),
        400: OpenApiResponse(description="Invalid request"),
        401: OpenApiResponse(description="Invalid or missing API key"),
        404: OpenApiResponse(description="Design system not found or MCP not enabled"),
    },
    description="Call an MCP tool on a design system",
    tags=["MCP"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def mcp_call_tool(request, design_system_id: str):
    """
    Call an MCP tool on a design system.
    
    This endpoint executes a tool call and returns the result
    for use by vibe coding assistants.
    """
    api_key = get_api_key_from_request(request)
    
    server = MCPDesignSystemServer(design_system_id, api_key)
    
    if not server.validate_api_key(api_key):
        return Response(
            {"error": _("Invalid or missing API key")},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tool_name = request.data.get('name')
    arguments = request.data.get('arguments', {})
    
    if not tool_name:
        return Response(
            {"error": _("Tool name is required")},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = server.call_tool(tool_name, arguments)
    
    if result.is_error:
        return Response(
            {"error": result.content[0]["text"]},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        "content": result.content
    })


@extend_schema(
    responses={
        200: OpenApiResponse(description="MCP configuration for the design system"),
        404: OpenApiResponse(description="Design system not found or MCP not enabled"),
    },
    description="Get MCP configuration for a design system",
    tags=["MCP"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def mcp_get_config(request, design_system_id: str):
    """
    Get MCP configuration for a design system.
    
    Returns the configuration needed to connect vibe coding tools
    to this design system's MCP server.
    
    Note: This endpoint requires the owner to be authenticated.
    """
    from ..models import DesignSystem
    
    try:
        design_system = DesignSystem.objects.get(id=design_system_id)
        
        # Check if requester is the owner
        if request.user.is_authenticated and request.user == design_system.user:
            config = get_design_system_mcp_config(design_system_id)
            
            if not config:
                return Response(
                    {"error": _("MCP not enabled for this design system")},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(config)
        else:
            return Response(
                {"error": _("Unauthorized")},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except DesignSystem.DoesNotExist:
        return Response(
            {"error": _("Design system not found")},
            status=status.HTTP_404_NOT_FOUND
        )
