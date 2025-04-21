from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from core.models import Plan
from core.serializers import PlanSerializer

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar planos ativos
    """
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]
