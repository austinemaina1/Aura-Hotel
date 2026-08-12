from django.urls import path
from . import views

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('add/', views.create_review, name='create_review'),
    path('edit/<int:id>/', views.edit_review, name='edit_review'),
    path('delete/<int:id>/', views.delete_review, name='delete_review'),

    path('dashboard/', views.review_dashboard, name='review_dashboard'),
]

