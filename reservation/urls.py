from django.urls import path
from . import views




urlpatterns = [
    path("", views.HomePatient, name="index"),
    path("doctors", views.HomeDoctor, name="doctorsindex"),
    path("admin", views.HomeAdmin, name="adminindex"),
    path("about", views.AboutUs, name="about"),
    path("contact", views.Contact, name="contact"),
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
    path('schedule', views.PatientSchedule, name='schedulept'),
    path('cancelcon/<str:pk>', views.CancelConsultation, name='cancelcon'),
    path('cancelfac/<str:pk>', views.CancelReservation, name='cancelfac'),


    # DOCTOR
    path("consultation_doctors", views.CheckConsultation, name="consultation_doctors"),
    path("upload_labresults/<str:pk>", views.UploadResults, name="upload_labresults"),
    path("consulhistory", views.ConsulsHistory, name="consulhistory"),
    path("profile_doctor", views.ProfileDoctor, name="profile_doctor"),
    path('editprofiledt/<str:pk>', views.EditProfileDoctor, name='editprofiledt'),
    path('scheduledoctor', views.DoctorSchedule, name='scheduledt'),
    path('approvecon/<str:pk>', views.ApproveConsultation, name='approvecon'),
    path('donecon/<str:pk>', views.DoneConsultation, name='donecon'),


    path('approvereservation/<str:pk>', views.ApproveReservation, name='approveres'),
    path('cancelreservation/<str:pk>', views.CancelReservationAdmin, name='cancelres'),
    path('donereservation/<str:pk>', views.DoneConsultation, name='doneres'),

    # Billing
    path('Checkout/', views.Checkout, name='checkout'),
    path('paypal-return/', views.paypal_return, name='paypal-return'),
    path('paypal-cancel/', views.paypal_cancel, name='paypal-cancel'),
    path('billing/', views.BillingList, name='billing'),

    # DOWNLOAD
    path('download/<int:document_id>/', views.download, name='download'),
    path('report/<int:pk>/', views.report, name='report'),
    # AUTH
    path("register/", views.Register, name="register"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    # ADMIN
    path('admin/', views.adminpage, name='admin'),
    path('adminreservation/', views.CheckReservation, name='adminreservation'),
    path('admincancelreservation/', views.CheckCancelReservation, name='admincancelreservation'),
    path('admindonereservation/<str:pk>', views.DoneReservation, name='admindoneres'),
    path("adminupload_labresults/<str:pk>", views.UploadResultsAdmin, name="adminupload_labresults"),
    path("reservation_historyadmin/", views.ReservationHistoryAdmin, name="reservation_historyadmin"),
    path("admin_schedule/", views.AdminSchedule, name="admin_schedule"),

    # Verify
    path('verify/<str:token>', views.Verify, name='verify'),
]



    