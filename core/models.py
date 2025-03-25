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
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
    
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_objects', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='updated_%(class)s_objects', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Account(BaseModel):
    # TYPE_CHOICES = [
    #     ('INCOME', 'Corrente'),
    #     ('EXPENDITURE', 'Poupança'),
    #     ('TRANSFER', 'Investimento'),
    #     ('TRANSFER', 'Outros')
    # ]
     
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    # type = models.CharField(max_length=30, default='INCOME', choices=TYPE_CHOICES)
    # bank = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Card(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
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
    
class Icon(BaseModel):
    name = models.CharField(max_length=100, default='')
    icon_svg = models.TextField(default='', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(BaseModel):
    name = models.CharField(max_length=100, default='')
    icon = models.TextField(default='', null=True, blank=True)
    # icon_obj = models.ForeignKey('Icon', null=True, on_delete=models.SET_NULL, default=None)  # Supondo que você tenha um modelo Category
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Transaction(BaseModel):
    # Campos principais da transação
    value = models.FloatField()
    value_installment = models.FloatField(default=0)
    description = models.CharField(max_length=255)
    account = models.ForeignKey('Account', null=True, on_delete=models.CASCADE)  # Supondo que você tenha um modelo Account
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
        ('INVESTMENT', 'Investment'),
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
