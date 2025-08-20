from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<slug:slug>', views.landing_page, name='landing_page'),
    path('search/', views.cars_search, name='cars_search'),
]