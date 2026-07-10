from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.history_view, name='history'),
    path('edit/<int:record_id>/', views.edit_record_view, name='edit_record'),
    path('delete/<int:record_id>/', views.delete_record_view, name='delete_record'),
    path('clear/', views.clear_history_view, name='clear_history'),
    path('export/', views.export_history_view, name='export_history'),
]
