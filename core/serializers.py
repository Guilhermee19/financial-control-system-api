from rest_framework import serializers
from drf_base64.fields import Base64ImageField, Base64FileField
from .models import *

class UserSerializer(serializers.ModelSerializer):
  profile_image = Base64ImageField(required=False)
  class Meta:
    model = User
    exclude = ['user_token', 'password', 'forgot_password_expire', 'forgot_password_hash']  # Exclui o campo 'password'
    # fields = ['id', 'last_login', 'username', 'email', 'is_active']
    
class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = '__all__'
    
class ContaSerializer(serializers.ModelSerializer):
  class Meta:
    model = Conta
    fields = '__all__'
    
class FinanceContaSerializer(serializers.ModelSerializer):
  class Meta:
    model = Conta
    exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']  # Exclui o campo 'password'

class FinanceCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ['id', 'bg_color', 'color', 'name', 'percent'] 
    
class FinanceSerializer(serializers.ModelSerializer):
  account_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  category_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  
  def get_account_obj(self, obj):
    if obj.account:
        return FinanceContaSerializer(obj.account).data
    return None
  
  def get_category_obj(self, obj):
    if obj.category:
        return FinanceCategorySerializer(obj.category).data
    return None
  
  class Meta:
    model = Finance
    fields = '__all__'
    
    
class InstallmentSerializer(serializers.ModelSerializer):
  installment_image = Base64ImageField(required=False)
  
  class Meta:
    model = Installment
    fields = '__all__'