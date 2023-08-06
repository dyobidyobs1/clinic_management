from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
import locale
import uuid

from django.core.files.storage import FileSystemStorage
from django.db import models

fs = FileSystemStorage(location="/pdf_file")


# locale.setlocale(locale.LC_ALL, 'fil-PH')



def create_rand_id():
        from django.utils.crypto import get_random_string
        return get_random_string(length=13, 
            allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')

class CustomUser(AbstractUser):
    is_doctor = models.BooleanField(default=False)

class ReservationSettings(models.Model):
    reservation_limit = models.IntegerField()
    reservation_current = models.IntegerField()

    def validate(self):
        if self.reservation_limit < self.reservation_current:
            return False
        elif self.reservation_limit == self.reservation_current:
            return True
        else:
            return True

    def __str__(self):
        return f'Limit: {self.reservation_limit} ------ Current: {self.reservation_current}'

# ADMIN
class Services(models.Model):
    service_name = models.CharField(max_length=255)
    service_description = models.TextField()
    service_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='uploads/services', blank=True, null=True)
    reservation_limit = models.IntegerField()
    reservation_current = models.IntegerField()

    def validate(self):
        if self.reservation_limit < self.reservation_current:
            return False
        elif self.reservation_limit == self.reservation_current:
            return False
        else:
            return True

    def price(self):
        # locale.setlocale(locale.LC_ALL, 'fil-PH')
        # return locale.currency(self.service_price, grouping=True)
        total_amount = float(self.service_price)
        total_amountstr = "{:,.2f}".format(total_amount)
        return total_amountstr

    def __str__(self):
        return f"{self.service_name} ₱{self.price()}"

class Facilites(models.Model):
    facility_name = models.CharField(max_length=255)
    facility_description = models.TextField()
    facility_price = models.DecimalField(max_digits=10, decimal_places=2)
    reservation_limit = models.IntegerField()
    reservation_current = models.IntegerField()

    def validate(self):
        if self.reservation_limit < self.reservation_current:
            return False
        elif self.reservation_limit == self.reservation_current:
            return True
        else:
            return True

    def price(self):
        locale.setlocale(locale.LC_ALL, 'fil-PH')
        return locale.currency(self.facility_price, grouping=True)

    def __str__(self):
        return f"{self.facility_name} {locale.currency(self.facility_price, grouping=True)}"

class Speciality(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

# DOCTOR
class DoctorDetails(models.Model):
    GENDER = (
        ("M", "Male"),
        ("F", "Female"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    bdate = models.DateTimeField(null=True, blank=True)
    placebirth = models.CharField(max_length=50, null=True, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE, null=True, blank=True)
    rndid = models.CharField(
        max_length=100, default=uuid.uuid4, editable=False, null=True, blank=True
    )

    def date(self):
        # locale.setlocale(locale.LC_ALL, 'en-US')
        return self.bdate.strftime("%B %d, %Y")
        
    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'

class Results(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.CharField(max_length=255)
    is_facility = models.BooleanField(default=False)
    result_file = models.FileField(storage=fs)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # locale.setlocale(locale.LC_ALL, 'en-US')
        date = self.date.strftime("%B %d, %Y")
        return f"A Result for {self.patient} on {date}"

class Prescription(models.Model):
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.CharField(max_length=255)
    is_facility = models.BooleanField(default=False)
    result_file = models.FileField(storage=fs)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # locale.setlocale(locale.LC_ALL, 'en-US')
        date = self.date.strftime("%B %d, %Y")
        return f"A Prescription for {self.patient} on {date}"


# PATIENT/USER
class UserDetails(models.Model):
    GENDER = (
        ("M", "Male"),
        ("F", "Female"),
    )

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True)
    middle_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=1, choices=GENDER, null=True)
    address = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=50, null=True)
    bdate = models.DateTimeField(null=True, blank=True)
    placebirth = models.CharField(max_length=50, null=True)
    is_verified = models.BooleanField(default=False)
    token = models.CharField(
        max_length=100, null=True, blank=True, editable=False
    )
    rndid = models.CharField(
        max_length=100, default=uuid.uuid4, editable=False, null=True, blank=True
    )

    def date(self):
        # locale.setlocale(locale.LC_ALL, 'en-US')
        return self.bdate.strftime("%B %d, %Y")

    def __str__(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'


class ReservationFacilities(models.Model):
    TS = (
        ("1", "6:00AM - 12:00NN"),
        ("2", "1:00PM - 6:00PM"),
    )


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.CharField(max_length=255)
    facility = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True)
    schedule = models.DateTimeField()
    reference_number = models.CharField(max_length=255, editable=False, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_approve = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_cancelled_by_admin = models.BooleanField(default=False)
    is_bill_generated = models.BooleanField(default=False)
    timeslot = models.CharField(max_length=1, choices=TS, default=1)

    def date(self):
        # locale.setlocale(locale.LC_ALL, 'en-US')
        return self.schedule.strftime("%B %d, %Y")

    def __str__(self):
        return f"{self.user} {self.facility}"


class ReserveConsulation(models.Model):
    TS = (
        ("1", "8-9AM"),
        ("2", "10-11AM"),
        ("3", "12-1PM"),
        ("4", "2-3PM"),
        ("5", "4-5PM"),
    )


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.CharField(max_length=255)
    speciality = models.CharField(max_length=255)
    doctor = models.CharField(max_length=255)
    doctors_id = models.CharField(max_length=255, null=True, blank=True)
    is_approve = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    schedule = models.DateTimeField()
    timeslot = models.CharField(max_length=1, choices=TS, null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def date(self):
        # locale.setlocale(locale.LC_ALL, 'en-US')
        return self.schedule.strftime("%B %d, %Y")
    
    def __str__(self):
        return f"Consultation for {self.user} with {self.doctor}"

class Billing(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    reference_number = models.CharField(max_length=255, editable=False, null=True, blank=True)
    transac_id = models.CharField(max_length=255, editable=False, null=True, blank=True)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    is_generated = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{(self.user.username.upper())} has a payable of {locale.currency(self.total_payment, grouping=True)} \
            with a Reference Number of {self.reference_number}"

    def price(self):
        # locale.setlocale(locale.LC_ALL, 'fil-PH')
        # return locale.currency(self.total_payment, grouping=True)
        total_amount = float(self.total_payment)
        total_amountstr = "{:,.2f}".format(total_amount)
        return total_amountstr

class Messages(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    to = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} has a message to {self.to}"

    
