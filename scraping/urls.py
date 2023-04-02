from django.urls import path
from . import views

urlpatterns = [
    path('', views.scraping_home, name='scraping_home'),
    path('scrape/', views.scrape, name='scrape'),
    path('woodland/', views.woodland_formations, name='woodland'),
]