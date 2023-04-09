from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import *
from .models import *

from django.db.models import Q

# Auth
def Register(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(request, "Account Created For " + user)
                return redirect("login")
            else:
                messages.info(request, "Make Sure your Credentials is Correct or Valid")
                messages.info(request, "Also make sure your credentials specially password is Secure")

        context = {"form": form}
    return render(request, "reservation/register.html", context)

def Login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            if request.user.is_superuser:
                return redirect("admin")
        elif request.user.is_doctor:
                return redirect("doctorsindex")
        else:
            return redirect("index")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    if user.is_superuser:
                        return redirect("admin")
                elif user.is_doctor:
                    return redirect("doctorsindex")
                else:
                    return redirect("index")
            else:
                messages.info(request, "Username or Password is Incorrect")

    context = {}
    return render(request, "reservation/login.html")


def Logout(request):
    logout(request)
    return redirect("login")

# Patient
@login_required(login_url="login")
def HomePatient(request):
    if request.user.is_staff:
        if request.user.is_superuser:
            return redirect("adminindex")
    elif request.user.is_doctor:
        return redirect("doctorsindex")
    else:
        return render(request, "reservation/patient/patient_home.html")

@login_required(login_url="login")
def AddReservation(request, pk):
    facility = Facilites.objects.get(id=pk)
    print("facility", facility)
    reservationform = ReservationFormFacilities()
    print("reservationform", reservationform)
    if request.method == "POST":
        reservationform = ReservationFormFacilities(request.POST)
        if reservationform.is_valid():
            reservationform.save(commit=False).user = request.user
            reservationform.save(commit=False).facility = facility
            reservationform.save()
        return redirect("index")
    context = {"form": reservationform, "details": facility}
    return render(request, "reservation/patient/add_reservation.html", context)

@login_required(login_url="login")
def ViewFacility(request):
    facility = Facilites.objects.all()
    context = {"details": facility}
    return render(request, "reservation/patient/view_reservation.html", context)

@login_required(login_url="login")
def ViewConsultation(request):
    doctors = DoctorDetails.objects.all()
    context = {"details": doctors}
    return render(request, "reservation/patient/view_consultation.html", context)

def AddConsultation(request, pk):
    doctor = DoctorDetails.objects.get(rndid=pk)
    consultationform = ReservationFormConsulation()
    if request.method == "POST":
        consultationform = ReservationFormConsulation(request.POST)
        print(consultationform)
        print(request.POST)
        print(request.POST)
        print(consultationform.is_valid())
        if consultationform.is_valid():
            consultationform.save(commit=False).user = request.user
            consultationform.save(commit=False).doctors_id = pk
            consultationform.save()
        return redirect("index")
    context = {"details": doctor, "form": consultationform}
    return render(request, "reservation/patient/add_consultation.html", context)


@login_required(login_url="login")
def PendingReservation(request):
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) | Q(is_approve=False))
    context = {"reservation": reservation}
    return render(request, "reservation/patient/pending_reservation.html", context)


@login_required(login_url="login")
def PendingConsultation(request):
    consultation = ReserveConsulation.objects.filter(Q(user=request.user) | Q(is_approve=False))
    context = {"reservation": consultation}
    return render(request, "reservation/patient/pending_consultation.html", context)


@login_required(login_url="login")
def ReservationHistory(request):
    return render(request, "reservation/patient/reservation_history.html")


@login_required(login_url="login")
def ConsulHistory(request):
    return render(request, "reservation/patient/consultation_history.html")


@login_required(login_url="login")
def LaboratoryResults(request):
    return render(request, "reservation/patient/laboratory_results.html")


@login_required(login_url="login")
def ProfilePatient(request):
    profile_details = UserDetails.objects.get(user=request.user)
    context = {"details": profile_details}
    return render(request, "reservation/patient/profile.html", context)

@login_required(login_url="login")
def EditProfilePatient(request, pk):
    profile_details = UserDetails.objects.get(rndid=pk)
    profile_form = UserProfileForm(instance=profile_details)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_details)
        if profile_form.is_valid():
            profile_form.save(commit=False).user = request.user
            profile_form.save()
            return redirect('profile_patient')
    context = {"form": profile_form}
    return render(request, "reservation/patient/edit_profile.html", context)

@login_required(login_url="login")
def MessagesPatient(request):
    messages = Messages.objects.filter(to=request.user).order_by('-date')
    context = {"messages": messages}
    return render(request, "reservation/patient/patient_messages.html", context)

# Doctors
@login_required(login_url="login")
def HomeDoctor(request):
    return render(request, "reservation/doctors/doctors_home.html")
    
@login_required(login_url="login")
def CheckConsultation(request):
    return render(request, "reservation/doctors/check_consultation.html")
    
@login_required(login_url="login")
def UploadResults(request):
    return render(request, "reservation/doctors/upload_results.html")

@login_required(login_url="login")
def ConsulsHistory(request):
    return render(request, "reservation/doctors/consultation_history.html")
    
@login_required(login_url="login")
def ProfileDoctor(request):
    return render(request, "reservation/doctors/doctors_profile.html")

@login_required(login_url="login")
def MessagesDoctor(request):
    return render(request, "reservation/doctors/messages_doctors.html")

# Admin/Staff
@login_required(login_url="login")
def adminpage(request):
    return HttpResponseRedirect(reverse('admin:index'))

@login_required(login_url="login")
def HomeAdmin(request):
    return render(request, "reservation/admin.html")