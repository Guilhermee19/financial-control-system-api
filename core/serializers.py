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
    
class FinanceContaSerializer(serializers.ModelSerializer):
  class Meta:
    model = Conta
    exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']  # Exclui o campo 'password'

class FinanceTagSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tag
    fields = ['id', 'bg_color', 'color', 'nome', 'porcent']  # Exclui o campo 'password'
    
class FinanceSerializer(serializers.ModelSerializer):
  account_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  tag_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  
  def get_account_obj(self, obj):
    if obj.account:
        return FinanceContaSerializer(obj.account).data
    return None
  
  def get_tag_obj(self, obj):
    if obj.tag:
        return FinanceTagSerializer(obj.tag).data
    return None
  
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