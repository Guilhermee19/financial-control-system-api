from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField

def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError(_('Users must have an email'))

        user = self.model(
            email=email,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )

        user.is_admin = True
        user.save(using=self._db)

        return user



class Plan(models.Model):
    title = models.CharField(max_length=255)
    monthly_price = models.FloatField(default=0)
    annual_price = models.FloatField(default=0)
    benefits = RichTextUploadingField(null=True, blank=True, default="")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

class User(AbstractBaseUser): 
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    forgot_password_hash = models.CharField(max_length=255, null=True, blank=True)
    forgot_password_expire = models.DateTimeField(null=True, blank=True)
    user_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_objects', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='updated_%(class)s_objects', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Account(BaseModel):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Conta"
        verbose_name_plural = "Contas"

class Card(BaseModel):
    card_type = models.CharField(max_length=10, choices=[('CREDIT', 'Crédito'), ('DEBIT', 'Débito')], default='DEBIT')
    number = models.CharField(max_length=16, unique=True)
    expiration_date = models.DateField()
    cardholder_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    credit_due_date = models.DateField()
    balance_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.card_type} - {self.cardholder_name}'
    
    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"
    
class Icon(BaseModel):
    name = models.CharField(max_length=100, default='')
    icon_svg = models.TextField(default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Icone"
        verbose_name_plural = "Icones"

class Category(BaseModel):
    name = models.CharField(max_length=100, default='')
    icon = models.TextField(default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
class Subcategory(BaseModel):
    name = models.CharField(max_length=100, default='')
    icon = models.TextField(default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Subcategoria"
        verbose_name_plural = "Subcategorias"
    
class Transaction(BaseModel):
    # Campos principais da transação
    value = models.FloatField()
    value_installment = models.FloatField(default=0)
    description = models.CharField(max_length=255)
    account = models.ForeignKey('Account', null=True, on_delete=models.CASCADE)  # Supondo que você tenha um modelo Account
    card = models.ForeignKey('Card', null=True, on_delete=models.CASCADE)  # Supondo que você tenha um modelo Account
    category = models.ForeignKey('Category', null=True, on_delete=models.SET_NULL)  # Supondo que você tenha um modelo Category
    expiry_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    date_payment = models.DateField(null=True, blank=True)
    receipt = models.ImageField(upload_to='installments/', null=True, blank=True)
    installments = models.IntegerField()
    current_installment = models.IntegerField(default=1)
    
    # Relacionamento com a própria transação
    related_transaction = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    # Tipo de transação (Receita, Despesa, Transferência, Investimento)
    TRANSACTION_TYPE_CHOICES = [
        ('INCOME', 'Receita'),
        ('EXPENDITURE', 'Despesa'),
        ('TRANSFER', 'Transferência'),
    ]
    type = models.CharField(max_length=12, choices=TRANSACTION_TYPE_CHOICES)

    # Frequência de recorrência (Única, Semanal, Mensal, Anual)
    RECURRENCE_CHOICES = [
        ('SINGLE', 'Single'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('ANNUAL', 'Yearly'),
        ('INSTALLMENTS', 'Installments'),
    ]
    recurrence = models.CharField(max_length=15, choices=RECURRENCE_CHOICES, default='single')

    def __str__(self):
        return f"{self.description} - {self.value} ({self.type})"
    
    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
