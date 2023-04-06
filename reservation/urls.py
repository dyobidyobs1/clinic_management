from django.urls import path
from . import views




urlpatterns = [
    path("", views.HomePatient, name="index"),
    path("doctors", views.HomeDoctor, name="doctorsindex"),
    path("admin", views.HomeAdmin, name="adminindex"),


    # PATIENT
    path("reservationform", views.AddReservation, name="reservation_add"),
    path("consultationform", views.AddConsultation, name="consultation_add"),
    path("reservation", views.PendingReservation, name="reservation"),
    path("consultation", views.PendingConsultation, name="consultation"),
    path("reservationhistory", views.ReservationHistory, name="reservation_history"),
    path("consultationhistory", views.ConsulHistory, name="consultation_history"),
    path("labresults", views.LaboratoryResults, name="labresults"),
    path("profile_patient", views.ProfilePatient, name="profile_patient"),

    # DOCTOR
    path("consultation_doctors", views.CheckConsultation, name="consultation_doctors"),
    path("upload_labresults", views.UploadResults, name="upload_labresults"),
    path("consulhistory", views.ConsulHistory, name="consulhistory"),
    path("profile_doctor", views.ProfileDoctor, name="profile_doctor"),
    
    # AUTH
    path("register/", views.Register, name="register"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    # ADMIN
    path('admin/', views.adminpage, name='admin'),
]



    