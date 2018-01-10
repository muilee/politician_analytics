from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
	path("<int:id>", views.politician, name="politician"),
    path("", views.index, name="index"),
]