from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('process/', views.process, name='process'),
    path('download/', views.download, name='download'),
    path('annotation/', views.annotation, name='annotation'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('tutoral/', views.tutoral, name='tutoral'),
]
