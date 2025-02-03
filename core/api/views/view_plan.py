from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from core.serializers import *

#?  ----------------------
#?  ------- PLANS --------
#?  ----------------------
@api_view(['GET'])
def get_all_plan(request):

    plans = Plan.objects.filter(is_active=True)
    serializer = PlanSerializer(plans, many=True)
    return Response(serializer.data)

