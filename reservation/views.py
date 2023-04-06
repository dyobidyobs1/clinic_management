from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import *
from .models import *

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
                return redirect("adminindex")
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
                        return redirect("adminindex")
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
    return render(request, "reservation/patient/patient_home.html")

@login_required(login_url="login")
def AddReservation(request):
    return render(request, "reservation/patient/add_reservation.html")


@login_required(login_url="login")
def AddConsultation(request):
    return render(request, "reservation/patient/add_consultation.html")


@login_required(login_url="login")
def PendingReservation(request):
    return render(request, "reservation/patient/pending_reservation.html")


@login_required(login_url="login")
def PendingConsultation(request):
    return render(request, "reservation/patient/pending_consultation.html")


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
    return render(request, "reservation/patient/profile.html")

# Doctors
@login_required(login_url="login")
def HomeDoctor(request):
    return render(request, "reservation/doctors/doctors_home.html")
    

def CheckConsultation(request):
    return render(request, "reservation/doctors/check_consultation.html")
    

def UploadResults(request):
    return render(request, "reservation/doctors/upload_results.html")


def ConsulHistory(request):
    return render(request, "reservation/doctors/consultation_history.html")
    

def ProfileDoctor(request):
    return render(request, "reservation/doctors/doctors_profile.html")

# Admin/Staff
@login_required(login_url="login")
def adminpage(request):
    return HttpResponseRedirect(reverse('admin:index'))

@login_required(login_url="login")
def HomeAdmin(request):
    return render(request, "reservation/admin.html")