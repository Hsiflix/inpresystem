from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('createNewText/', views.create_text_button, name = 'create_text_button'),
    path('find/', views.find_button, name = 'find_button'),
    path('sort/', views.sort_button, name = 'sort_button'),
    path('save_<int:text_id>/', views.save_text, name = 'save_text'),
    path('view_<int:text_id>/', views.review_text, name = 'review_text'),
    path('delete_<int:text_id>/', views.delete_text, name = 'delete_text'),
    path('created/', views.create_text, name = 'create_text')
]