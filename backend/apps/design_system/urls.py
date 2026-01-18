"""
URL configuration for design system generation and management API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .mcp import views as mcp_views

app_name = 'design_system'

# Create router for ViewSet
router = DefaultRouter()
router.register('', views.DesignSystemViewSet, basename='design-system')

urlpatterns = [
    # Design system CRUD and management (ViewSet)
    path('systems/', include(router.urls)),
    
    # Legacy endpoints for backward compatibility
    path(
        'generate/',
        views.generate_design_system,
        name='generate'
    ),
    
    # Task management
    path(
        'tasks/<str:task_id>/',
        views.get_task_status,
        name='task-status'
    ),
    path(
        'tasks/<str:task_id>/cancel/',
        views.cancel_task,
        name='task-cancel'
    ),
    
    # Provider information
    path(
        'providers/',
        views.list_providers,
        name='list-providers'
    ),
    
    # MCP endpoints
    path(
        'mcp/<str:design_system_id>/tools/',
        mcp_views.mcp_list_tools,
        name='mcp-tools'
    ),
    path(
        'mcp/<str:design_system_id>/call/',
        mcp_views.mcp_call_tool,
        name='mcp-call'
    ),
    path(
        'mcp/<str:design_system_id>/config/',
        mcp_views.mcp_get_config,
        name='mcp-config'
    ),
]
