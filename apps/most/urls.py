from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('query/', views.query, name='query'),
    # path('ajaxzj/', views.ajaxzj, name='ajaxzj'),
    path('<int:pk>/detail/', views.detail, name='detail'),
]