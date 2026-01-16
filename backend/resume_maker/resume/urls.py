from django.urls import path
from django.urls import include
from . import views


urlpatterns = [
    path('get_resume/', views.ResumeView.as_view(), name='get_resume'),
    path('get_json/', views.ResumeJsonView.as_view(), name='get_json'),
    path('get_pdf_from_json/', views.ResumePdfFromJsonView.as_view(), name='get_pdf_from_json'),
    path('get_data/', views.ResumeDataView.as_view(), name='get_data'),
]
