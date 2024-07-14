from django.contrib.auth.models import User
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_objects', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name='updated_%(class)s_objects', on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Tag(models.Model):
    color = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    porcent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nome

class Conta(BaseModel):
    name = models.CharField(max_length=100)
    balance_debit = models.DecimalField(max_digits=10, decimal_places=2)
    balance_credit = models.DecimalField(max_digits=10, decimal_places=2)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    credit_due_date = models.DateField()
    is_debit = models.BooleanField()
    is_credit = models.BooleanField()


    def __str__(self):
        return self.name

class Finance(BaseModel):
    TAG_CHOICES = [
        ('C', 'Compra'),
        ('G', 'Gasto'),
        ('CF', 'Conta Fixa'),
        ('I', 'Investimento'),
    ]
    
    tag = models.CharField(max_length=2, choices=TAG_CHOICES)
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    account = models.ForeignKey(Conta, on_delete=models.CASCADE)
    is_cash = models.BooleanField()
    is_installments = models.BooleanField()
    number_of_installments = models.IntegerField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.tag} - {self.value}"

class Parcela(models.Model):
    finance = models.ForeignKey(Finance, related_name='installments', on_delete=models.CASCADE)
    installment_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_installment = models.IntegerField()

    def __str__(self):
        return f"{self.finance} - Installment {self.current_installment}"

class FinanceEntry(BaseModel):
    REPEAT_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('card', 'Card'), ('conta', 'Conta')])
    description = models.CharField(max_length=255)
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES)

    def __str__(self):
        return f"{self.type} - {self.value}"
