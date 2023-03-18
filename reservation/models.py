from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Services(models.Model):
    service_name = models.CharField(max_length=255)
    service_description = models.TextField()
    service_price = models.DecimalField(max_digits=6, decimal_places=2)


    def __str__(self):
        return f"{self.service_name} {self.service_price}"

class Facilites(models.Model):
    facility_name = models.CharField(max_length=255)
    facility_description = models.TextField()
    facility_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.facility_name} {self.facility_price}"


# Patients/User
class ReservationServices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    services = models.ManyToManyField(Services)
    schedule = models.DateTimeField()

    def date(self):
        return self.schedule.strftime("%B %d %Y")

    def __str__(self):
        return f"{self.user} {self.services.count()}"


class ReservationFacilities(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    facility = models.ManyToManyField(Facilites)
    schedule = models.DateTimeField()

    def date(self):
        return self.schedule.strftime("%B %d %Y")

    def __str__(self):
        return f"{self.user} {self.facility.count()}"



# Admin/Doctor
