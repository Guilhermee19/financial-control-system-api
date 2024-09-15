from webbrowser import get
from django.urls import path    
from .views import *     

urlpatterns = [     
    path('auth/', auth_user),
    path('social-network/', social_network),
    path('get-user/', get_user),
    
    #? CRUD User
    path('all-users/', get_all_users),
    path('user-by-id/', get_user_by_id),
    path('create-user/', post_user),
    
    #? CRUD Tag
    path('all-tags/', get_all_tags),
    path('tag-by-id/', get_tag_by_id),
    path('create-tag/', post_tag),
    path('edit-tag/', update_tag),
    path('delete-tag/<int:id>/', delete_tag),
    
    #? CRUD Conta
    path('all-accounts/', get_all_contas),
    path('account-by-id/', get_conta_by_id),
    path('create-account/', post_conta),
    path('edit-account/', update_conta),
    path('delete-account/<int:id>/', delete_conta),
    
    #? CRUD Finance
    path('all-finances/', get_all_finances),
    path('finance-by-id/', get_finance_by_id),
    path('create-finance/', post_finance),
    path('edit-finance/', update_finance),
    path('delete-finance/<int:id>/', delete_finance),
    
    #? CRUD Parcela
    path('all-parcela/', get_parcela),
    # path('finance_entry/', get_finance_entry),
]                                           
