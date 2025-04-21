from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import User
from core.serializers import UserSerializer


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        method='post',
        operation_description="Login do usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, example="user@example.com"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, example="123456"),
            },
        ),
        responses={200: "Token gerado com sucesso"},
    )

    @action(detail=False, methods=["post"])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"detail": "Email e senha são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email, is_deleted=False)
        except User.DoesNotExist:
            return Response({"detail": "E-mail ou senha incorretos."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active or user.is_deleted:
            return Response({"detail": "Usuário inativo ou deletado."}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response({"detail": "E-mail ou senha incorretos."}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        })

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data["password"])
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response({
            "errors": serializer.errors,
            "message": "Erro ao validar os dados do usuário."
        }, status=status.HTTP_400_BAD_REQUEST)
