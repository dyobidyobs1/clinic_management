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


from django.http import FileResponse
from fpdf import  FPDF


# Paypal
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings

# Paypal Integration
@login_required(login_url="login")
def Checkout(request):
    host = request.get_host()
    invoice_str = create_rand_id()
    locale.setlocale(locale.LC_ALL, 'fil-PH')
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) and 
        Q(is_approve=True)).filter(is_done=False).filter(is_cancelled=False).filter(is_bill_generated=False)
    
    total_amount = 0
    for res in reservation:
        total_amount += res.facility.facility_price

    total_amountstr = locale.currency(total_amount, grouping=True)

    billing = Billing.objects.filter(reference_number=invoice_str)
    print(len(billing))
    if len(billing) == 0:
        Billing.objects.create(
            user=request.user,
            reference_number=invoice_str,
            total_payment=total_amount
        )
        for res in reservation:
            reservations = ReservationFacilities.objects.get(id=res.id)
            reservations.reference_number = invoice_str
            reservations.save()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % total_amount,
        'item_name': 'Reservation Payment',
        'invoice': invoice_str,
        'currency_code': 'PHP',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host, reverse('paypal-return')),
        'cancel_return': 'http://{}{}'.format(host, reverse('paypal-cancel')),
    }
    
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"reservation": reservation, "total_amount": total_amountstr, "form" : form}
    return render(request, "reservation/patient/check_out_patient.html", context)

@login_required(login_url="login")
def paypal_return(request):
    messages.success(request, 'You\'ve successfully made a payment!')
    return redirect('index')

@login_required(login_url="login")
def paypal_cancel(request):
    messages.error(request, 'You cancel your transaction')
    return redirect('index')


@login_required(login_url="login")
def BillingList(request):
    bill = Billing.objects.filter(Q(request=request.user) and Q(is_generated = True)).order_by("-date_created")
    context = {"results": bill}
    return render(request, "reservation/patient/billing.html", context)


# Print PDF
@login_required(login_url="login")
def report(request, pk):
    bill_generated = Billing.objects.get(id=pk)
    res = ReservationFacilities.objects.filter(reference_number=bill_generated.reference_number).filter(is_bill_generated=True)

    locale.setlocale(locale.LC_ALL, 'fil-PH')
    total_amountstr = locale.currency(bill_generated.total_payment, grouping=True)
    pdf = FPDF('P', 'mm', (114.63, 119.71))
    pdf.add_page()
    pdf.add_font("DejaVuSans", fname="DejaVuSans.ttf")
    pdf.set_font("DejaVuSans", size=16)
    pdf.cell(40, 10, '',0,1)
    pdf.set_font("DejaVuSans", size=12)
    pdf.cell(100, 8, f"{'Invoice Number'.ljust(20)}  {bill_generated.reference_number.rjust(10)}", 0, 1)
    pdf.cell(100, 9, f"{'Transaction Number'.ljust(20)}  {bill_generated.transac_id.rjust(10)}", 0, 1)
    pdf.cell(100, 10, f"{'Total Amount'.ljust(20)}  {total_amountstr.rjust(10)}", 0, 1)
    for line in res:
        text = str(line.facility.price())
        pdf.cell(100, 8, f"Facility: {line.facility.facility_name.ljust(20)}", 0, 1)
        pdf.cell(100, 10, f"Price: {text.rjust(20)} Schedule: {line.date().ljust(10)}", 0, 1)
        pdf.line(1, 38, 119, 38)

    pdf.output(f'{bill_generated.reference_number}.pdf', 'F')
    return FileResponse(open(f'{bill_generated.reference_number}.pdf', 'rb'), as_attachment=True, content_type='application/pdf')
    
# AUTH
def Register(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            if request.user.is_superuser:
                return redirect("adminindex")
        elif request.user.is_doctor:
                return redirect("doctorsindex")
        else:
            return redirect("index")
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

@login_required(login_url="login")
def AddConsultation(request, pk):
    doctor = DoctorDetails.objects.get(rndid=pk)
    patient = UserDetails.objects.get(user=request.user)
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
    context = {"details": doctor, "form": consultationform, "patient": patient}
    return render(request, "reservation/patient/add_consultation.html", context)


@login_required(login_url="login")
def PendingReservation(request):
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) & 
        Q(is_approve=False)).filter(is_cancelled=False).order_by('schedule').order_by('date_created')
    context = {"reservation": reservation}
    return render(request, "reservation/patient/pending_reservation.html", context)


@login_required(login_url="login")
def PendingConsultation(request):
    consultation = ReserveConsulation.objects.filter(Q(user=request.user) & 
        Q(is_approve=False)).filter(is_cancelled=False).order_by('schedule').order_by('date_created')
    context = {"reservation": consultation}
    return render(request, "reservation/patient/pending_consultation.html", context)

@login_required(login_url="login")
def CancelConsultation(request, pk):
    approveConsul = ReserveConsulation.objects.get(id=pk)
    approveConsul.is_cancelled = True
    
    approveConsul.save()
    Messages.objects.create(
        user=request.user,
        to=approveConsul.user,
        message=f"Your Consultation is Succesfully Cancelled")
    return redirect("consultation")

@login_required(login_url="login")
def CancelReservation(request, pk):
    approvefacility = ReservationFacilities.objects.get(id=pk)
    approvefacility.is_cancelled = True
    approvefacility.is_cancelled_by_admin = True
    approvefacility.save()
    Messages.objects.create(
        user=request.user,
        to=approvefacility.user,
        message=f"Your Reservation is Succesfully Cancelled")
    return redirect("reservation")


@login_required(login_url="login")
def ReservationHistory(request):
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) and 
        Q(is_done=True)  | Q(is_cancelled=True))
    context = {"reservation": reservation}
    return render(request, "reservation/patient/reservation_history.html", context)


@login_required(login_url="login")
def ConsulHistory(request):
    consultation = ReserveConsulation.objects.filter(Q(user=request.user) and 
        Q(is_done=True) | Q(is_cancelled=True))
    context = {"reservation": consultation}
    return render(request, "reservation/patient/consultation_history.html", context)


@login_required(login_url="login")
def LaboratoryResults(request):
    fullname = f'{request.user.userdetails.first_name} {request.user.userdetails.middle_name} {request.user.userdetails.last_name}'
    results = Results.objects.filter(patient=fullname).order_by("-date")
    print(results)
    context = {"results": results}
    return render(request, "reservation/patient/laboratory_results.html", context)


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

@login_required(login_url="login")
def PatientSchedule(request):
    consultation = ReservationFacilities.objects.filter(
        Q(user=request.user) and Q(is_approve=True)).filter(is_done=False).filter(is_cancelled_by_admin=False).filter(is_bill_generated=True).order_by('-schedule')
    context = {"reservation": consultation}
    return render(request, "reservation/patient/patient_schedule.html", context)

# Doctors
@login_required(login_url="login")
def HomeDoctor(request):
    if request.user.is_staff:
        if request.user.is_superuser:
            return redirect("adminindex")
    elif not request.user.is_doctor:
        return redirect("index")
    else:
        return render(request, "reservation/doctors/doctors_home.html")
    
@login_required(login_url="login")
def CheckConsultation(request):
    doctordetails = DoctorDetails.objects.get(user=request.user)
    consultation = ReserveConsulation.objects.filter(Q(doctors_id=doctordetails.rndid) | 
        Q(is_approve=False)).order_by('-date_created')
    print(consultation)
    context = {"reservation": consultation}
    return render(request, "reservation/doctors/check_consultation.html", context)

@login_required(login_url="login")
def ApproveConsultation(request, pk):
    approveConsul = ReserveConsulation.objects.get(id=pk)
    approveConsul.is_approve = True
    approveConsul.save()
    Messages.objects.create(
        user=request.user,
        to=approveConsul.user,
        message=f"Your Consultation Schedule has been approved by \
            {approveConsul.doctor}",
        )
    return redirect("consultation_doctors")

@login_required(login_url="login")
def DoneConsultation(request, pk):
    approveConsul = ReserveConsulation.objects.get(id=pk)
    approveConsul.is_done = True
    approveConsul.save()
    Messages.objects.create(
        user=request.user,
        to=approveConsul.user,
        message=f"Your Consultation is Done the Results will be \
            Uploaded if there is one",
        )
    return redirect("scheduledt")
    
@login_required(login_url="login")
def UploadResults(request, pk):
    consultation = ReserveConsulation.objects.get(id=pk)
    uploadresultform = UploadResultsForm()
    print(uploadresultform)
    if request.method == "POST":
        uploadresultform = UploadResultsForm(request.POST, request.FILES)
        print(uploadresultform)
        print(uploadresultform.is_valid())
        if uploadresultform.is_valid():
            uploadresultform.save(commit=False).doctor = request.user
            uploadresultform.save()
        return redirect("consulhistory")
    context = {"reservation": consultation, "form" : uploadresultform}
    return render(request, "reservation/doctors/upload_results.html", context)

@login_required(login_url="login")
def ConsulsHistory(request):
    doctordetails = DoctorDetails.objects.get(user=request.user)
    consultation = ReserveConsulation.objects.filter(Q(doctors_id=doctordetails.rndid) and
        Q(is_done=True)).order_by('-date_created')
    print(consultation)
    context = {"reservation": consultation}
    return render(request, "reservation/doctors/consultation_history.html", context)
    
@login_required(login_url="login")
def ProfileDoctor(request):
    profile_details = DoctorDetails.objects.get(user=request.user)
    context = {"details": profile_details}
    return render(request, "reservation/doctors/doctors_profile.html", context)

def EditProfileDoctor(request, pk):
    profile_details = DoctorDetails.objects.get(rndid=pk)
    profile_form = DoctorProfileForm(instance=profile_details)

    if request.method == 'POST':
        profile_form = DoctorProfileForm(request.POST, request.FILES, instance=profile_details)
        if profile_form.is_valid():
            profile_form.save(commit=False).user = request.user
            profile_form.save()
            return redirect('profile_doctor')
    context = {"form": profile_form}
    return render(request, "reservation/doctors/edit_profile.html", context)

@login_required(login_url="login")
def MessagesDoctor(request):
    return render(request, "reservation/doctors/messages_doctors.html")

@login_required(login_url="login")
def DoctorSchedule(request):
    doctordetails = DoctorDetails.objects.get(user=request.user)
    consultation = ReserveConsulation.objects.filter(
        Q(doctors_id=doctordetails.rndid) and Q(is_done=False)).filter(is_approve=True)
    print(consultation)
    context = {"reservation": consultation}
    return render(request, "reservation/doctors/doctors_schedule.html", context)

# Admin/Staff
@login_required(login_url="login")
def adminpage(request):
    return HttpResponseRedirect(reverse('admin:index'))

@login_required(login_url="login")
def HomeAdmin(request):
    return render(request, "reservation/admin.html")

@login_required(login_url="login")
def ApproveReservation(request, pk):
    approveConsul = ReservationFacilities.objects.get(id=pk)
    approveConsul.is_approve = True
    approveConsul.save()
    Messages.objects.create(
        user=request.user,
        to=approveConsul.user,
        message=f"Your Reservation Schedule has been approved by \
            {request.user}",
        )
    return redirect("adminreservation")

@login_required(login_url="login")
def CancelReservationAdmin(request, pk):
    approvefacility = ReservationFacilities.objects.get(id=pk)
    approvefacility.is_cancelled_by_admin = True
    approvefacility.is_cancelled = True
    approvefacility.save()
    Messages.objects.create(
        user=request.user,
        to=approvefacility.user,
        message=f"Your Reservation is Cancelled by Admin")
    return redirect("admincancelreservation")


@login_required(login_url="login")
def DoneReservation(request, pk):
    approveConsul = ReservationFacilities.objects.get(id=pk)
    approveConsul.is_done = True
    approveConsul.save()
    Messages.objects.create(
        user=request.user,
        to=approveConsul.user,
        message=f"Your Reservation is Done the Results will be \
            Uploaded if there is one",
        )
    return redirect("admin")

@login_required(login_url="login")
def CheckReservation(request):
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) and 
        Q(is_approve=False)).filter(is_cancelled=False).order_by('schedule').order_by('date_created')
    context = {"reservation": reservation}
    return render(request, "reservation/reservation_admin.html", context)

@login_required(login_url="login")
def CheckCancelReservation(request):
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) and 
        Q(is_approve=True)).filter(is_cancelled_by_admin=False).order_by('schedule').order_by('date_created')
    context = {"reservation": reservation}
    return render(request, "reservation/reservation_admin_cancel.html", context)

@login_required(login_url="login")
def UploadResultsAdmin(request):
    uploadresultform = UploadResultsForm()
    print(uploadresultform)
    if request.method == "POST":
        uploadresultform = UploadResultsForm(request.POST, request.FILES)
        print(uploadresultform)
        print(uploadresultform.is_valid())
        if uploadresultform.is_valid():
            uploadresultform.is_facilty = True
            uploadresultform.save(commit=False).doctor = request.user
            uploadresultform.save()
        return redirect("adminreservation")
    context = {"form" : uploadresultform}
    return render(request, "reservation/upload_results_admin.html", context)


# Download

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def download(request, document_id):
    document = get_object_or_404(Results, pk=document_id)
    response = HttpResponse(document.result_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.result_file.name}"'
    return response
