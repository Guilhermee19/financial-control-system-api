from django.contrib import admin    # importar o path "caminho"
from django.urls import path, include    # importar o path "caminho"

from . import views     # importa as informações do arquivo views.py

urlpatterns = [     # lista de padrões de url
    path('user/', views.get_user, name='get_all_users'),     # caminho q mostra o retorno 
    path('tag/', views.get_tag, name='get_all_tags'),     # caminho q mostra o retorno 
    path('conta/', views.get_conta, name='get_all_contas'),     # caminho q mostra o retorno 
    path('finance/', views.get_finance, name='get_all_finances'),     # caminho q mostra o retorno 
    path('parcela/', views.get_parcela, name='get_all_parcelas'),     # caminho q mostra o retorno 
    path('finance_entry/', views.get_finance_entry, name='get_all_finance_entrys'),     # caminho q mostra o retorno 
]                                           
