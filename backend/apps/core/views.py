from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from .serializers import HealthCheckSerializer


@extend_schema(
    responses={200: HealthCheckSerializer},
    description="Health check endpoint"
)
@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint to verify the API is running.
    """
    return Response({
        'status': 'healthy',
        'message': _('API is running successfully')
    })
