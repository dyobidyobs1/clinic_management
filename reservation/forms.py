from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import ModelForm
from .models import *


class DateInput(forms.DateInput):
    input_type = "date"


class CreateUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]
        # fields = ["username", "password1", "password2"]


class ReservationFormFacilities(forms.ModelForm):
    class Meta:
        model = ReservationFacilities
        fields = "__all__"

        widgets = {"schedule": DateInput()}


class ReservationFormConsulation(forms.ModelForm):
    class Meta:
        model = ReserveConsulation
        fields = "__all__"

        widgets = {"schedule": DateInput()}

class ResultsForm(forms.ModelForm):
    class Meta:
        model = Results
        fields = "__all__"

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ["first_name", "middle_name", "last_name", "gender", "address", "email", "bdate", "placebirth"]

        widgets = {"bdate": DateInput()}

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorDetails
        fields = "__all__"

        widgets = {"bdate": DateInput()}

class UploadResultsForm(forms.ModelForm):
    class Meta:
        model = Results
        fields = "__all__"

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = "__all__"