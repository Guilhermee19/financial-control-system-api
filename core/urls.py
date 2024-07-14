from django.urls import path    # importar o path "caminho"
from . import views     # importa as informações do arquivo views.py

urlpatterns = [     # lista de padrões de url
    path('', views.index, name='index')     # caminho q mostra o retorno 
]                                           #  da function Index
