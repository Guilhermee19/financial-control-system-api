from webbrowser import get
from django.urls import path    
from .views import *     

urlpatterns = [     
    # User
    path('all-users/', get_all_users),
    path('user-by-id/', get_user_by_id),
    path('create-user/', post_user),
    
    
    # Tag
    path('all-tags/', get_all_tags),
    path('tag-by-id/', get_tag_by_id),
    path('create-tag/', post_tag),
    
    # path('tags/', get_all_tags),
    # path('conta/', get_conta),
    # path('finance/', get_finance),
    # path('parcela/', get_parcela),
    # path('finance_entry/', get_finance_entry),
]                                           
