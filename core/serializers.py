from rest_framework import serializers

from .models import *

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    exclude = ['user_token', 'password', 'forgot_password_expire', 'forgot_password_hash']  # Exclui o campo 'password'
    # fields = ['id', 'last_login', 'username', 'email', 'is_active']
    
class TagSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tag
    fields = '__all__'
    
class ContaSerializer(serializers.ModelSerializer):
  class Meta:
    model = Conta
    fields = '__all__'
    
class FinanceSerializer(serializers.ModelSerializer):
  class Meta:
    model = Finance
    fields = '__all__'
    
class ParcelaSerializer(serializers.ModelSerializer):
  class Meta:
    model = Parcela
    fields = '__all__'
    
class FinanceEntrySerializer(serializers.ModelSerializer):
  class Meta:
    model = FinanceEntry
    fields = '__all__'