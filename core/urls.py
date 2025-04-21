from rest_framework.routers import DefaultRouter 
from core.views import *

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'plans', PlanViewSet, basename='plans')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'cards', CardViewSet, basename='cards')
router.register(r'accounts', AccountViewSet, basename='accounts')

urlpatterns = router.urls