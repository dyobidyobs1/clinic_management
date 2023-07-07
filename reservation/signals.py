from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received

from .models import *
from .views import report
from .utils import *

from django.http import FileResponse
from fpdf import  FPDF

import locale


@receiver(valid_ipn_received)
def payment_received(sender, **kwargs):
    print("test valid")
    ipn_obj = sender
    limit = ReservationSettings.objects.all()
    if ipn_obj.payment_status == 'Completed':
        bill_generated = Billing.objects.get(reference_number=ipn_obj.invoice)
        if limit[0].validate:
            bill_generated.transac_id = ipn_obj.txn_id
            bill_generated.is_generated = True
            bill_generated.save()
            Billing.objects.filter(is_generated=False).delete()

            res = ReservationFacilities.objects.filter(reference_number=ipn_obj.invoice)
            for r in res:
                reservation = ReservationFacilities.objects.get(id=r.id)
                reservation.is_approve = True
                reservation.is_bill_generated = True
                reservation.save()
            
            Messages.objects.create(
            user=bill_generated.user,
            to=bill_generated.user,
            message=f"You Successfully Paid your Reservations and this is the Invoice {ipn_obj.invoice} \
                and the Paypal Transaction ID {ipn_obj.txn_id}")
            
            # Email
            subject = f'Invoice {ipn_obj.invoice}'
            message = f"You Successfully Paid your \n Reservations and this is the Invoice {ipn_obj.invoice}\
                \n and the  Paypal Transaction ID {ipn_obj.txn_id}"

            recipients = [bill_generated.user.email, ]

                
            send_email(subject, message, recipients)
        else:
            Messages.objects.create(
            user=bill_generated.user,
            to=bill_generated.user,
            message=f"The Reservation Limit is Fulfilled")


            # Email
            subject = f'The Reservation Limit is Fulfilled'
            message = f"Your Payment is not Successfull because the Reservation Limit is Fulfilled"

            recipients = [bill_generated.user.email, ]
     
            send_email(subject, message, recipients)

        print("test valid")
        print(ipn_obj.invoice)
        print(ipn_obj.mc_gross)
        
@receiver(invalid_ipn_received)
def payment_not_received(sender, **kwargs):
    print("test failed")
    ipn_obj = sender
    # bill_generated = Billing.objects.get(reference=ipn_obj.invoice)
    # bill_generated.transac_id = ipn_obj.txn_id
    # bill_generated.is_generated = True
    # bill_generated.save()
    if ipn_obj.payment_status != 'Completed':
        # Billing.objects.create()
        print("test failed")
