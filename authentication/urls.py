from django.urls import path

from authentication import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_change/done/', views.custom_logout, name='password_change_done'),
    path('password_reset', views.custom_logout, name='password_reset'),
    path('reset/<uidb64>/<token>', views.custom_logout, name='password_reset_confirm'),
    path('reset/done', views.custom_logout, name='password_reset_complete'),
]
