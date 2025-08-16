from django.urls import path
from . import views

urlpatterns = [
    path("", views.CarListView.as_view(), name="cars_list"),
    path("<slug:slug>", views.CarDetailView.as_view(), name="car_detail"),
    path("new/", views.car_create, name="car_create"),
    path("edit/<slug:slug>", views.car_update, name="car_update"),
    path("delete/<slug:slug>", views.car_delete, name="car_delete"),
    path("favorite/<slug:slug>", views.favorite_toggle, name="favorite_toggle"),
    path("mes-favorits/", views.my_favorites, name="my_favorites"),

]
