from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import *
from .models import *
from .utils import *

from django.db.models import Q


from django.http import FileResponse
from fpdf import  FPDF

import time


# Paypal
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings

# Paypal Integration
@login_required(login_url="login")
def Checkout(request):
    host = request.get_host()
    invoice_str = create_rand_id()
    # locale.setlocale(locale.LC_ALL, 'fil-PH')
    current = 0
    total_amount = 0
    form = []
    reservations = ReservationFacilities.objects.filter(Q(user=request.user) and 
        Q(is_approve=False)).filter(is_done=False).filter(is_cancelled=False).filter(is_bill_generated=False)
    
    billing = Billing.objects.filter(reference_number=invoice_str)
    
    for i in reservations:
        current = int(i.facility.reservation_current + 1)
        i.facility.reservation_current = current
        if current <= int(i.facility.reservation_limit):
            total_amount += i.facility.service_price
            if len(billing) == 0:
                Billing.objects.create(
                    user=request.user,
                    reference_number=invoice_str,
                    total_payment=total_amount
                )
                for res in reservations:
                    reser = ReservationFacilities.objects.get(id=res.id)
                    reser.reference_number = invoice_str
                    reser.save()

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

        else:
            print("reservation limit meet")
            messages.info(request, "Reservation Exceed to Limit")

            Messages.objects.create(
            user=request.user,
            to=request.user,
            message=f"The Reservation Limit for today is Fulfilled")


            # Email
            subject = f'The Reservation Limit is Fulfilled'
            message = f"Your Payment is not Successfull because the Reservation Limit is Fulfilled"

            recipients = [request.user.email, ]
        
            send_email(subject, message, recipients)

    # total_amountstr = locale.currency(total_amount, grouping=True)
    total_amount = float(total_amount)
    total_amountstr = "{:,.2f}".format(total_amount)

    context = {"reservation": reservations, "total_amount": total_amountstr, "form" : form}
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
    bill = Billing.objects.filter(user=request.user).filter(is_generated=True).order_by("-date_created")
    context = {"results": bill}
    return render(request, "reservation/patient/billing.html", context)


# Print PDF
@login_required(login_url="login")
def report(request, pk):
    bill_generated = Billing.objects.get(id=pk)
    res = ReservationFacilities.objects.filter(reference_number=bill_generated.reference_number).filter(is_bill_generated=True)

    # locale.setlocale(locale.LC_ALL, 'fil-PH')
    # total_amountstr = locale.currency(bill_generated.total_payment, grouping=True)

    total_amount = float(bill_generated.total_payment)
    total_amountstr = "{:,.2f}".format(total_amount)
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
        pdf.cell(100, 8, f"Services: {line.facility.service_name.ljust(20)}", 0, 1)
        pdf.cell(100, 10, f"Price: ₱{text.rjust(20)} Schedule: {line.date().ljust(10)}", 0, 1)
        pdf.cell(100, 12, f"Timeslot: {line.get_timeslot_display()}", 0, 1)
        pdf.line(1, 38, 119, 38)

    pdf.output(f'{bill_generated.reference_number}.pdf', 'F')
    return FileResponse(open(f'{bill_generated.reference_number}.pdf', 'rb'), as_attachment=True, content_type='application/pdf')

# Home Page
def HomePage(request):
    return render(request, "reservation/homepage.html")

# AUTH
def Register(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            if request.user.is_superuser:
                return redirect("adminindex")
        elif request.user.is_doctor:
                return redirect("consultation_doctors")
        else:
            return redirect("index")
    else:
        random_id = create_rand_id()
        host = request.get_host()
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                username = form.save()
                print(username)
                user = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                messages.success(request, "Account Created For " + user)
                messages.success(request, "Please verify your Email in " + email)
                UserDetails.objects.create(user=username, token=random_id)
                send_email_token(email, random_id, host)
                return redirect("login")
            else:
                messages.info(request, "Make Sure your Credentials is Correct or Valid")
                messages.info(request, "Also make sure your credentials specially password is Secure")

        context = {"form": form}
    return render(request, "reservation/register.html", context)

def Login(request):
    # subject = 'TEST Subject'
    # message = 'Test Message'
    # recipients = ['joaquinzaki21@gmail.com']
    # test_send(subject, message, recipients)


    if request.user.is_authenticated:
        if request.user.is_staff:
            if request.user.is_superuser:
                return redirect("adminindex")
        elif request.user.is_doctor:
                return redirect("consultation_doctors")
        else:
            return redirect("index")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                userDet = UserDetails.objects.filter(user=user)
                if userDet:
                    if not userDet[0].is_verified:
                        messages.info(request, "Your Account is Not Verified")
                    else:
                        login(request, user)
                        return redirect("index")
                else:
                    login(request, user)
                    if user.is_staff:
                        if user.is_superuser:
                            return redirect("adminindex")
                    elif user.is_doctor:
                        return redirect("consultation_doctors")
                    else:
                        return redirect("index")
            else:
                messages.info(request, "Username or Password is Incorrect")

    context = {}
    return render(request, "reservation/login.html")


def Logout(request):
    logout(request)
    return redirect("login")

def AboutUs(request):
    return render(request, "reservation/about_us.html")

def Contact(request):
    return render(request, "reservation/contact.html")

# Patient
@login_required(login_url="login")
def HomePatient(request):
    if request.user.is_staff:
        if request.user.is_superuser:
            return redirect("adminindex")
    elif request.user.is_doctor:
        return redirect("consultation_doctors")
    else:
        return render(request, "reservation/patient/patient_home.html")

@login_required(login_url="login")
def AddReservation(request, pk):
    facility = Services.objects.get(id=pk)
    patient = UserDetails.objects.get(user=request.user)
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
    context = {"form": reservationform, "details": facility, "patient": patient}
    return render(request, "reservation/patient/add_reservation.html", context)

@login_required(login_url="login")
def ViewFacility(request):
    facility = Services.objects.all()
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
    reservation = ReservationFacilities.objects.filter(user=request.user).filter(Q(is_done=True)  | Q(is_cancelled=True))
    print(reservation)
    print(request.user)
    context = {"reservation": reservation}
    return render(request, "reservation/patient/reservation_history.html", context)


@login_required(login_url="login")
def ConsulHistory(request):
    consultation = ReserveConsulation.objects.filter(user=request.user).filter(Q(is_done=True) | Q(is_cancelled=True))
    context = {"reservation": consultation}
    return render(request, "reservation/patient/consultation_history.html", context)


@login_required(login_url="login")
def LaboratoryResults(request):
    fullname = f'{request.user.userdetails.last_name}, {request.user.userdetails.first_name} {request.user.userdetails.middle_name}'
    results = Results.objects.filter(patient=fullname).order_by("-date")
    print(results)
    context = {"results": results}
    return render(request, "reservation/patient/laboratory_results.html", context)

@login_required(login_url="login")
def PrescriptionList(request):
    fullname = f'{request.user.userdetails.last_name}, {request.user.userdetails.first_name} {request.user.userdetails.middle_name}'
    results = Prescription.objects.filter(patient=fullname).order_by("-date")
    context = {"results": results}
    return render(request, "reservation/patient/perscription.html", context)

@login_required(login_url="login")
def ProfilePatient(request):
    random_id = create_rand_id()
    context = {}
    profile_details = UserDetails.objects.filter(user=request.user)
    print(profile_details)
    if  profile_details:
        if profile_details[0].rndid:
            context = {"details": profile_details[0]}
    else:
        UserDetails.objects.create(user=request.user, rndid=random_id)
        profile_details = UserDetails.objects.filter(user=request.user)
        context = {"details": profile_details[0]}
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
    print(request.user.email)
    messages = Messages.objects.filter(to=request.user).order_by('-date')
    context = {"messages": messages}
    return render(request, "reservation/patient/patient_messages.html", context)

@login_required(login_url="login")
def PatientSchedule(request):

    # consultation = ReservationFacilities.objects.filter(
    #     Q(user=request.user) and Q(is_approve=True)).filter(is_done=False).filter(is_cancelled_by_admin=False).filter(is_bill_generated=True).order_by('schedule')
    consultation = ReservationFacilities.objects.filter(
        Q(user=request.user)).filter(is_approve=True).filter(is_done=False).\
            filter(is_cancelled_by_admin=False).filter(is_bill_generated=True).order_by('schedule')
    consultation2 = ReserveConsulation.objects.filter(
        Q(user=request.user)).filter(is_approve=True).filter(is_done=False).order_by('schedule').order_by('timeslot')
    print(request.user)
    print(consultation)
    context = {"reservation": consultation, "reservation2": consultation2}
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
    consultation = ReserveConsulation.objects.filter(doctors_id=doctordetails.rndid).filter(is_approve=False).filter(is_cancelled=False).order_by('-date_created')
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
def UploadPerscrip(request, pk):
    consultation = ReserveConsulation.objects.get(id=pk)
    uploadresultform = PrescriptionForm()
    print(uploadresultform)
    if request.method == "POST":
        uploadresultform = PrescriptionForm(request.POST, request.FILES)
        print(uploadresultform)
        print(uploadresultform.is_valid())
        if uploadresultform.is_valid():
            uploadresultform.save(commit=False).doctor = request.user
            uploadresultform.save()
        return redirect("consulhistory")
    context = {"reservation": consultation, "form" : uploadresultform}
    return render(request, "reservation/doctors/perscription.html", context)


@login_required(login_url="login")
def ConsulsHistory(request):
    users = CustomUser.objects.filter(is_superuser=False).filter(is_doctor=False)
    doctordetails = DoctorDetails.objects.get(user=request.user)
    consultation = ReserveConsulation.objects.filter(doctors_id=doctordetails.rndid).filter(is_done=True).order_by('-date_created')
    print(consultation)
    context = {"reservation": consultation, "users": users}
    if request.method == "POST":
        patient_filter = request.POST.get("patient_filter")
        if patient_filter:
            # patient_filter2 = CustomUser.objects.get(id=int(patient_filter))
            consultation = ReserveConsulation.objects.filter(Q(patient__icontains=patient_filter)).filter(is_done=True).order_by('-date_created')
            context = {"reservation": consultation, "users": users}
    return render(request, "reservation/doctors/consultation_history.html", context)
    
@login_required(login_url="login")
def ProfileDoctor(request):
    random_id = create_rand_id()
    context = {}
    profile_details = DoctorDetails.objects.filter(user=request.user)
    print(profile_details)
    if  profile_details:
        if profile_details[0].rndid:
            context = {"details": profile_details[0]}
    else:
        DoctorDetails.objects.create(user=request.user, rndid=random_id)
        profile_details = DoctorDetails.objects.filter(user=request.user)
        context = {"details": profile_details[0]}
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
        Q(doctors_id=doctordetails.rndid) and Q(is_done=False)).filter(is_approve=True).order_by('schedule').order_by('timeslot')
    print(consultation)
    context = {"reservation": consultation}
    return render(request, "reservation/doctors/doctors_schedule.html", context)

@login_required(login_url="login")
def ResultsHistoryDocView(request):
    users = CustomUser.objects.filter(is_superuser=False).filter(is_doctor=False)
    results = []
    context = {"results": results, "users": users}
    if request.method == "POST":
        patient_filter = request.POST.get("patient_filter")
        if patient_filter:
            # patient_filter2 = CustomUser.objects.get(id=int(patient_filter))
            # fullname = f'{patient_filter2.userdetails.last_name}, {patient_filter2.userdetails.first_name} {patient_filter2.userdetails.middle_name}'
            results = Results.objects.filter(Q(patient__icontains=patient_filter)).order_by("-date")
            print(patient_filter)
            # print(patient_filter2)
            context = {"results": results, "users": users}
    print(results)
    print(request.user)
    return render(request, "reservation/doctors/patients_history_services.html", context)


@login_required(login_url="login")
def PrescriptionHistoryDocView(request):
    users = CustomUser.objects.filter(is_superuser=False).filter(is_doctor=False)
    results = []
    context = {"results": results, "users": users}
    if request.method == "POST":
        patient_filter = request.POST.get("patient_filter")
        if patient_filter:
            # patient_filter2 = CustomUser.objects.get(id=int(patient_filter))
            # fullname = f'{patient_filter2.userdetails.last_name}, {patient_filter2.userdetails.first_name} {patient_filter2.userdetails.middle_name}'
            # results = Prescription.objects.filter(patient=fullname).order_by("-date")
            results = Prescription.objects.filter(Q(patient__icontains=patient_filter)).order_by("-date")
            print(patient_filter)
            print(results)
            # print(patient_filter2)
            context = {"results": results, "users": users}
    return render(request, "reservation/doctors/patients_history_consultation.html", context)

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
    return redirect("adminindex")

@login_required(login_url="login")
def CheckReservation(request):
    reservation = ReservationFacilities.objects.filter(Q(user=request.user) and 
        Q(is_approve=False)).filter(is_cancelled=False).order_by('schedule').order_by('date_created')
    context = {"reservation": reservation}
    return render(request, "reservation/reservation_history.html", context)

@login_required(login_url="login")
def CheckCancelReservation(request):
    reservation = ReservationFacilities.objects.filter(Q(is_approve=True)).filter(is_cancelled_by_admin=False).order_by('schedule')
    context = {"reservation": reservation}
    return render(request, "reservation/reservation_admin_cancel.html", context)

@login_required(login_url="login")
def AdminSchedule(request):
    consultation = ReservationFacilities.objects.filter(Q(is_done=False)).filter(is_approve=True)
    print(consultation)
    context = {"reservation": consultation}
    return render(request, "reservation/admin_schedule.html", context)

@login_required(login_url="login")
def ReservationHistoryAdmin(request):
    users = CustomUser.objects.filter(is_superuser=False).filter(is_doctor=False)
    consultation = ReservationFacilities.objects.filter(Q(is_done=True)).order_by('-date_created')
    context = {"reservation": consultation, "users": users}
    if request.method == "POST":
        patient_filter = request.POST.get("patient_filter")
        if patient_filter:
            # patient_filter2 = CustomUser.objects.get(id=int(patient_filter))
            print(patient_filter)
            # print(patient_filter2)
            consultation = ReservationFacilities.objects.filter(Q(patient__icontains=patient_filter)).filter(is_done=True).order_by('-date_created')
            context = {"reservation": consultation, "users": users}
    print(consultation)
    print(users)
    return render(request, "reservation/reservation_admin.html", context)

@login_required(login_url="login")
def AddReservationForm(request, pk):
    users = CustomUser.objects.get(id=pk)
    print(users)
    patient = UserDetails.objects.get(id=users.userdetails.id)
    filter_services = []
    facility = Services.objects.all()
    for i in facility:
        if i.validate():
            filter_services.append(i)
            
    print("facility", facility)
    reservationform = ReservationFormFacilities()
    print("reservationform", reservationform)
    if request.method == "POST":
        reservationform = ReservationFormFacilities(request.POST)
        facilityget = request.POST.get("facility")
        facility = Services.objects.get(id=facilityget)
        facility.reservation_current = int(facility.reservation_current + 1)
        if reservationform.is_valid():
            reservationform.save(commit=False).user = users
            reservationform.save(commit=False).facility = facility
            reservationCurr = reservationform.save()
            reservation = ReservationFacilities.objects.get(id=reservationCurr.id)
            reservation.is_approve = True
            reservation.save()
            facility.save()
        return redirect("index")
    context = {"form": reservationform, "filter_services": filter_services, "patient": patient}
    return render(request, "reservation/reservation_manual.html", context)

@login_required(login_url="login")
def AddReservationAdmin(request):
    users = CustomUser.objects.filter(is_superuser=False).filter(is_doctor=False)
    context = {"users": users}
    if request.method == "POST":
        patient_filter = request.POST.get("patient_filter")
        if patient_filter:
            # patient_filter2 = CustomUser.objects.get(id=int(patient_filter))
            print(patient_filter)
            # print(patient_filter2)
            users = CustomUser.objects.filter(
                Q(userdetails__first_name__icontains=patient_filter)  |
                Q(userdetails__middle_name__icontains=patient_filter) |
                Q(userdetails__last_name__icontains=patient_filter)).filter(is_superuser=False).filter(is_doctor=False)
            context = {"users": users}
    print(users)
    return render(request, "reservation/reservation_add_admin.html", context)

@login_required(login_url="login")
def ResetServices(request):
    services = Services.objects.all()
    if request.method == "POST":
        for i in services:
            i.reservation_current = 0
            i.save()
        return redirect("adminindex")
    return render(request, "reservation/confirmation_reset.html")



@login_required(login_url="login")
def UploadResultsAdmin(request, pk):
    reservation = ReservationFacilities.objects.get(id=pk)
    uploadresultform = UploadResultsForm()
    print(uploadresultform)
    if request.method == "POST":
        uploadresultform = UploadResultsForm(request.POST, request.FILES)
        print(uploadresultform)
        print(uploadresultform.is_valid())
        if uploadresultform.is_valid():
            uploadresultform.save(commit=False).is_facility = True
            uploadresultform.save(commit=False).doctor = request.user
            uploadresultform.save()
        return redirect("reservation_historyadmin")
    context = {"reservation": reservation, "form" : uploadresultform}
    return render(request, "reservation/upload_results_admin.html", context)



# Download
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def download(request, document_id):
    document = get_object_or_404(Results, pk=document_id)
    response = HttpResponse(document.result_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.result_file.name}"'
    return response

def downloadperscrption(request, document_id):
    document = get_object_or_404(Prescription, pk=document_id)
    response = HttpResponse(document.result_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.result_file.name}"'
    return response

# Verify Email
def Verify(request, token):
    try:
        userDetails = UserDetails.objects.get(token=token)
        userDetails.is_verified = True
        userDetails.save()
        messages.success(request, "Your Email is Verified!!!!")
        return redirect('login')

    
    except Exception as e:
        messages.info(request, "Invalid Token")
        return redirect('login')
    
def ContactUs(request):
    return render(request, "reservation/contact.html")
