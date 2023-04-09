from django.urls import path
from . import views




urlpatterns = [
    path("", views.HomePatient, name="index"),
    path("doctors", views.HomeDoctor, name="doctorsindex"),
    path("admin", views.HomeAdmin, name="adminindex"),
    path("messagesdoctor", views.MessagesDoctor, name="messagesdoctor"),
    path("messagespatient", views.MessagesPatient, name="messagespatient"),


    # PATIENT
    path("reservationform/<str:pk>", views.AddReservation, name="reservation_add"),
    path("reservationview", views.ViewFacility, name="reservation_view"),
    path("consultationview", views.ViewConsultation, name="consultation_view"),
    path("consultationform/<str:pk>", views.AddConsultation, name="consultation_add"),
    path("reservation", views.PendingReservation, name="reservation"),
    path("consultation", views.PendingConsultation, name="consultation"),
    path("reservationhistory", views.ReservationHistory, name="reservation_history"),
    path("consultationhistory", views.ConsulHistory, name="consultation_history"),
    path("labresults", views.LaboratoryResults, name="labresults"),
    path("profile_patient", views.ProfilePatient, name="profile_patient"),
    path('editprofile/<str:pk>', views.EditProfilePatient, name='editprofilept'),

    # DOCTOR
    path("consultation_doctors", views.CheckConsultation, name="consultation_doctors"),
    path("upload_labresults", views.UploadResults, name="upload_labresults"),
    path("consulhistory", views.ConsulsHistory, name="consulhistory"),
    path("profile_doctor", views.ProfileDoctor, name="profile_doctor"),
    
    # AUTH
    path("register/", views.Register, name="register"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    # ADMIN
    path('admin/', views.adminpage, name='admin'),
]



    