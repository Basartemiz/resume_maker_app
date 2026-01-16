from django.urls import path
from django.urls import include
from . import views


urlpatterns = [
    path('get_resume/', views.get_resume, name='get_resume'),
    path('get_json/', views.get_json, name='get_json'),
    path('get_pdf_from_json/', views.get_pdf_from_json, name='get_pdf_from_json'),
]
