from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.item_list),             # GET 목록, POST 생성
    path('items/<int:item_id>/', views.item_detail),  # GET, PUT, DELETE
]