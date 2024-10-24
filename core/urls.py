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
    path('update-user/', update_user),
    
    #? CRUD Category
    path('all-categories/', get_all_categories),
    path('category-by-id/', get_category_by_id),
    path('create-category/', post_category),
    path('edit-category/<int:id>/', update_category),
    path('delete-category/<int:id>/', delete_category),
    
    #? CRUD Account
    path('all-accounts/', get_all_accounts),
    path('account-by-id/', get_account_by_id),
    path('create-account/', post_account),
    path('edit-account/', update_account),
    path('delete-account/<int:id>/', delete_account),
    
    #? CRUD Card
    path('all-card/', get_all_cards),
    # path('account-by-id/', get_account_by_id),
    # path('create-account/', post_account),
    # path('edit-account/', update_account),
    # path('delete-account/<int:id>/', delete_account),
    
    #? CRUD Transaction
    path('all-transaction/', get_all_transaction),
    path('transaction-by-id/', get_transaction_by_id),
    path('create-transaction/', post_transaction),
    path('edit-transaction/<int:transaction>/', update_transaction),
    path('delete-transaction/<int:id>/', delete_transaction),
    
    #? CRUD Installment
    path('all-installment/', get_installment),
    path('pay-installment/', pay_installment),
    path('upload-installment-image/', upload_installment_image),
    
    #? Dashboard
    path('get-dashboard/', get_dashboard),
]                                           
