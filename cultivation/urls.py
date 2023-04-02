from django.urls import path
from . import views


urlpatterns = [
    path('monotub_whatever/', views.monotub_whatever, name='monotub_whatever'),
    path('get_data/', views.GetDataView.as_view(), name='get_data'),
    path('add_data/', views.AddDataView.as_view(), name='add_data'),
    path('crop/', views.crop, name='crop' ),
    path('harvest_form/', views.harvest_form, name='harvest_form'),
]