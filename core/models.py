from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from drf_base64.fields import Base64ImageField, Base64FileField

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
    
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_objects', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='updated_%(class)s_objects', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Account(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

# Cartões (vinculados às contas)
class Card(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='cards')
    card_type = models.CharField(max_length=10, choices=[('CREDIT', 'Crédito'), ('DEBIT', 'Débito')], default='DEBIT')
    number = models.CharField(max_length=16, unique=True)
    expiration_date = models.DateField()
    cardholder_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    credit_due_date = models.DateField()
    balance_credit = models.DecimalField(max_digits=10, decimal_places=2)
    card_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.card_type} - {self.cardholder_name}'
    
class Category(BaseModel):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20)
    bg_color = models.CharField(max_length=20, default='#f0f2f8')
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
    
class Transaction(BaseModel):
    TYPE_CHOICES = [
        ('INCOME', 'Receita'),
        ('EXPENDITURE', 'Despesa'),
        ('TRANSFER', 'Transferência')
    ]
      
    REPEAT_CHOICES = [
        ('SINGLE', 'Único'),
        ('WEEKLY', 'Semanal'),
        ('MONTHLY', 'Mensal'),
        ('ANNUAL', 'Anual'),
        ('INSTALLMENTS', 'Parcelada'),
    ]

    date = models.DateField(null=True, blank=True)
    value = models.FloatField()
    number_of_installments = models.IntegerField()
    description = models.CharField(max_length=255)
    type = models.CharField(max_length=30, default='INCOME', choices=TYPE_CHOICES)
    recurrence = models.CharField(max_length=30, default='DAILY', choices=REPEAT_CHOICES)
    
    def __str__(self):
        return f"{self.id} - {self.description}"

class Installment(BaseModel):
    transaction = models.ForeignKey(Transaction, related_name='installments', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    installment_value = models.FloatField()
    current_installment = models.IntegerField()
    total_installments = models.IntegerField(default=1)
    due_date  = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    payment_date  = models.DateField(null=True, blank=True)
    receipt = models.ImageField(upload_to='installments/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.transaction} - Installment {self.current_installment}"

