from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from .models import *

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'timestamp', 'is_read']
        
class UserSerializer(serializers.ModelSerializer):
  profile_image = Base64ImageField(required=False)
  
  plan_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  
  def get_plan_obj(self, obj):
    if obj.plan:
        return PlanSerializer(obj.plan).data
    return None
  
  class Meta:
    model = User
    exclude = ['user_token', 'password', 'forgot_password_expire', 'forgot_password_hash']  # Exclui o campo 'password'
    # fields = ['id', 'last_login', 'username', 'email', 'is_active']
    
class PlanSerializer(serializers.ModelSerializer):
  class Meta:
    model = Plan
    fields = '__all__' 
    
    
class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = '__all__'
    

class CardAccountSerializer(serializers.ModelSerializer):
  class Meta:
    model = Account
    exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']  # Exclui o campo 'password'
    
  
class CardSerializer(serializers.ModelSerializer):
  account_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  
  def get_account_obj(self, obj):
    if obj.account:
        return CardAccountSerializer(obj.account).data
    return None
  
  class Meta:
    model = Card
    fields = '__all__'
  
class AccountSerializer(serializers.ModelSerializer):
  cards = CardSerializer(many=True, read_only=True)  # Assumindo que você tenha um relacionamento reverso
  class Meta:
    model = Account
    fields = '__all__'  # Ou especifique os campos que você deseja incluir
        
        
class TransactionAccountSerializer(serializers.ModelSerializer):
  class Meta:
    model = Account
    exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']  # Exclui o campo 'password'

class TransactionCategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']  # Exclui o campo 'password'
    
class TransactionSerializer(serializers.ModelSerializer):
  account_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  category_obj = serializers.SerializerMethodField()  # Aqui você usa o serializer aninhado
  
  def get_account_obj(self, obj):
    if obj.account:
        return TransactionAccountSerializer(obj.account).data
    return None
  
  def get_category_obj(self, obj):
    if obj.category:
        return TransactionCategorySerializer(obj.category).data
    return None
  
  class Meta:
    model = Transaction
    fields = '__all__'
    
    
