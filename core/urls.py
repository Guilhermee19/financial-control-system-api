from webbrowser import get
from django.urls import path   
from rest_framework.routers import DefaultRouter 
# from .views import *     
from core.api.views import *     

router = DefaultRouter()

urlpatterns = [     
    path('auth/', auth_user),
    path('get-user/', get_user),
    
    #? CRUD User
    path('all-users/', get_all_users),
    path('user-by-id/', get_user_by_id),
    path('create-user/', post_user),
    path('update-user/', update_user),
    
    #? CRUD Plan
    path('all-plan/', get_all_plan),
    
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
    path('create-transaction/', create_transaction),
    path('edit-transaction/<int:transaction_id>/', update_transaction),
    path('delete-transaction/<int:id>/', delete_transaction),
    path('pay-transaction/', pay_transaction),
    
    #? Dashboard
    path('get-dashboard/', get_dashboard),
    path('get-dashboard-category/', get_dashboard_category),
    path('get-dashboard-expenditure-income/', get_dashboard_expenditure_income),
    path('get-dashboard-upcoming-and-unpaid-transactions/', get_upcoming_and_unpaid_transactions),
]                                           
