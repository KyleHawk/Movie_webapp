from django.contrib import admin
from django.urls import path, re_path

from movie_website import views
from django.conf import settings



app_name = "movie_website"
urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout),
    path('detail/<int:movie_no>', views.detail, name='detail'),
    path('action/', views.action_filter, name='action'),
    path('drama/', views.drama_filter, name='drama'),
    path('crime/', views.crime_filter, name='crime'),
    path('fantasy/', views.fantasy_filter, name='fantasy'),
    path('top10/', views.top_10, name='top10'),
    path('upload/', views.upload, name='upload'),
    path('order/', views.place_order, name='order'),
    path('order_status/', views.order_status, name='order_status'),
    path('findpwdView/', views.findpwdView),
    path('forgotPwd/', views.forgotPwd),
    path('ratings/', views.rating),
]



