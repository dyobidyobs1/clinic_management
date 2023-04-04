from django.urls import path
from . import views




urlpatterns = [
    path("", views.HomePatient, name="index"),
    path("doctors", views.HomeDoctor, name="doctorsindex"),
    path("admin", views.HomeAdmin, name="adminindex"),
    
    # AUTH
    path("register/", views.Register, name="register"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    # ADMIN
    path('admin/', views.adminpage, name='admin'),
]



    