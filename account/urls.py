from django.contrib import admin
from django.urls import path
from .views import RegisterView, LoginView, UserProfileView,StoreCreationView

urlpatterns = [
    # path('account/', include('account.urls')),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('create_store/', StoreCreationView.as_view(), name='create_store'),
    # path('logout/', LogoutView.as_view(), name='logout'),

]
