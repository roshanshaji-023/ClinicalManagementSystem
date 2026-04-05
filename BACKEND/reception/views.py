from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from decimal import Decimal
from datetime import datetime,time
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from administration.models import Doctor
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone




from .models import Appointment,Billing
from authentication.permissions import IsReceptionist
from .permissions import IsDoctorOrReceptionist


from datetime import datetime, timedelta  
from django.utils import timezone

from authentication.permissions import (
    IsReceptionist, IsDoctor, IsLabTechnician
)

from django.utils import timezone
from datetime import datetime
from django.db.models import Q

from administration.models import Doctor
from .models import (
    Patient, Appointment, WaitingToken,
    PatientHistory, Billing
)

from .serializers import (
    PatientSerializer, AppointmentSerializer,
    WaitingTokenSerializer, PatientHistorySerializer,
    BillingSerializer
)


# -------------------- PATIENT --------------------

class RegisterPatient(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        serializer = PatientSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                staff=getattr(request.user, 'staff', None)
            )
            return Response(serializer.data)

        return Response(serializer.errors)


class SearchPatient(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request):
        query = request.GET.get('q', '')

        patients = Patient.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )

        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)


class UpdatePatient(APIView):
    permission_classes = [IsReceptionist]

    def put(self, request, patient_id):

        patient = get_object_or_404(Patient, patient_id=patient_id)

        # Only allow updating specific fields
        allowed_fields = ['phone_number', 'address']

        data = {
            key: value for key, value in request.data.items()
            if key in allowed_fields
        }

        if not data:
            return Response({"error": "No valid fields provided"})

        serializer = PatientSerializer(patient, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Patient updated successfully"})

        return Response(serializer.errors)

class DeletePatient(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request, patient_id):

        patient = get_object_or_404(Patient, patient_id=patient_id)

        #  Prevent deletion if active appointments exist
        active_appointments = Appointment.objects.filter(
            patient=patient,
            status__in=["Scheduled", "Waiting", "In Consultation"]
        )

        if active_appointments.exists():
            return Response({"error": "Cannot delete patient with active appointments"})

        patient.is_active = False
        patient.save()

        return Response({"message": "Patient deactivated successfully"})
    

class DoctorAvailability(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request):

        doctor_id = request.GET.get("doctor")
        date = request.GET.get("date")

        # 🔴 Validate input
        if not doctor_id or not date:
            return Response({"error": "doctor and date required"})

        # 🔴 Convert string → date safely
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"})

        # 🔴 Get doctor
        doctor = get_object_or_404(Doctor, doctor_id=doctor_id, status='active')

        # 🟢 Fixed slots (can upgrade later)
        slots = [
            "09:00", "10:00", "11:00",
            "12:00", "14:00", "15:00", "16:00"
        ]

        # 🔵 Fetch booked slots correctly
        booked_queryset = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date_obj
        ).values_list('appointment_time', flat=True)

        booked = [t.strftime("%H:%M") for t in booked_queryset]

        # 🟢 Available slots
        available = [slot for slot in slots if slot not in booked]

        return Response({
            "doctor": f"{doctor.user.first_name} {doctor.user.last_name}",
            "date": str(date_obj),
            "available_slots": available,
            "booked_slots": booked
        })
    


class PatientProfile(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request, patient_id):

        patient = get_object_or_404(Patient, patient_id=patient_id)

        appointments = Appointment.objects.filter(
            patient=patient
        ).select_related('doctor')

        return Response({
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "phone": patient.phone_number,
            "gender": patient.gender,
            "date_of_birth": patient.date_of_birth,
            "blood_group": patient.blood_group,
            "address": patient.address,
            "is_active": patient.is_active,

            "appointments": [
                {
                    "appointment_id": a.appointment_id,
                    "doctor_name": f"{a.doctor.user.first_name} {a.doctor.user.last_name}",
                    "date": a.appointment_date,
                    "time": a.appointment_time,
                    "status": a.status,
                }
                for a in appointments
            ]
        })
# -------------------- APPOINTMENT --------------------

class CreateAppointment(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        data = request.data.copy()

        doctor = get_object_or_404(
            Doctor,
            doctor_id=data.get("doctor"),
            status='active'
        )

        serializer = AppointmentSerializer(data=data)

        if serializer.is_valid():
            serializer.save(
                created_by=request.user,
                doctor=doctor,
                staff=getattr(request.user, 'staff', None)
            )
            return Response(serializer.data)

        return Response(serializer.errors)

class SearchAppointments(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request):

        doctor = request.GET.get("doctor")
        status = request.GET.get("status")
        date = request.GET.get("date")

        appointments = Appointment.objects.all()

        if doctor:
            appointments = appointments.filter(doctor__doctor_id=doctor)

        if status:
            appointments = appointments.filter(status=status)

        if date:
            appointments = appointments.filter(appointment_date=date)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class AppointmentByDate(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request):
        date_param = request.GET.get("date")

        appointments = Appointment.objects.filter(
            appointment_date=date_param
        )

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    


class RescheduleAppointment(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):

        appointment = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("appointment")
        )

        #  Cannot reschedule completed
        if appointment.status in ["Completed", "In Consultation"]:
            return Response({"error": "Cannot reschedule this appointment"})

        try:
            new_date = datetime.strptime(
                request.data.get("appointment_date"), "%Y-%m-%d"
            ).date()

            new_time = datetime.strptime(
                request.data.get("appointment_time"), "%H:%M"
            ).time()
        except:
            return Response({"error": "Invalid date/time format"})

        #  Prevent double booking
        exists = Appointment.objects.filter(
            doctor=appointment.doctor,
            appointment_date=new_date,
            appointment_time=new_time
        ).exclude(pk=appointment.pk)

        if exists.exists():
            return Response({"error": "Slot already booked"})

        #  Update
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = "Scheduled"
        appointment.save()

        return Response({"message": "Appointment rescheduled"})


class CancelAppointment(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        appointment = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("appointment")
        )

        if appointment.status == "Completed":
            return Response({"error": "Cannot cancel completed appointment"})

        #  ADDED THIS BLOCK
        reason = request.data.get("reason")
        if not reason:
            return Response({"error": "Cancellation reason required"})

        #  THEN SET VALUES
        appointment.status = "Cancelled"
        appointment.cancellation_reason = reason
        appointment.save()

        return Response({"message": "Appointment cancelled"})
    





#-----------------FOLLOW-UP-----------------

class CreateFollowUp(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):

        parent = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("parent_appointment")
        )

        #  Must be completed
        if parent.status != "Completed":
            return Response({"error": "Follow-up allowed only after completion"})

        # Prevent duplicate follow-up
        if parent.follow_ups.exists():
            return Response({"error": "Follow-up already exists"})

        # Parse date/time
        try:
            appointment_date = datetime.strptime(
                request.data.get("appointment_date"), "%Y-%m-%d"
            ).date()

            appointment_time = datetime.strptime(
                request.data.get("appointment_time"), "%H:%M"
            ).time()
        except:
            return Response({"error": "Invalid date/time format"})

        # No past booking
        if appointment_date < timezone.localdate():
            return Response({"error": "Cannot book in past"})

        # Optional: 30-day rule
        if (appointment_date - parent.appointment_date).days > 30:
            return Response({"error": "Follow-up should be within 30 days"})

        appointment = Appointment.objects.create(
            patient=parent.patient,
            doctor=parent.doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            visit_type="Follow-Up",
            parent_appointment=parent,
            status="Scheduled",
            created_by=request.user,
            staff=getattr(request.user, 'staff', None)
        )

        return Response({
            "appointment_id": appointment.appointment_id,
            "linked_to": parent.appointment_id,
            "status": appointment.status
        })
    
#----------------Appointment Detail-----------------

class AppointmentDetail(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request, appointment_id):
        appointment = get_object_or_404(Appointment, appointment_id=appointment_id)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    


class PatientAppointments(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request, patient_id):

        appointments = Appointment.objects.filter(
            patient__patient_id=patient_id
        ).select_related('doctor', 'patient').prefetch_related('follow_ups').order_by('-appointment_date')

        serializer = AppointmentSerializer(appointments, many=True)

        return Response(serializer.data)


# -------------------- WALK-IN --------------------


class WalkIn(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        data = request.data

        phone = data.get("phone_number")

        try:
            dob = datetime.strptime(
                data.get("date_of_birth"), "%Y-%m-%d"
            ).date()
        except:
            return Response({"error": "Invalid date format"})

        patient, created = Patient.objects.get_or_create(
            phone_number=phone,
            defaults={
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "date_of_birth": dob,
                "gender": data.get("gender"),
                "blood_group": data.get("blood_group"),
                "address": data.get("address"),
                "created_by": request.user,
                "staff": getattr(request.user, 'staff', None)  
            }
        )

        doctor = get_object_or_404(
            Doctor,
            doctor_id=data.get("doctor"),
            status='active'
        )

        #  FIX: avoid "time in past" error + clean time format
        raw_time = timezone.localtime() + timedelta(minutes=5)

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=timezone.localdate(),
            appointment_time=raw_time.replace(second=0, microsecond=0).time(),  
            visit_type="New",
            status="Waiting",
            created_by=request.user,
            staff=getattr(request.user, 'staff', None)
)

        # Token auto-created via signal
        token = WaitingToken.objects.filter(appointment=appointment).first()

        return Response({
            "patient_id": patient.patient_id,
            "appointment_id": appointment.appointment_id,
            "token": token.token_number if token else None
        })


# -------------------- DOCTOR --------------------


from .permissions import IsDoctorOrReceptionist  # new permission

class DoctorQueue(APIView):
    permission_classes = [IsDoctorOrReceptionist]

    def get(self, request):
        user = request.user

        # ✅ DEBUG (optional)
        print(user, getattr(user, "staff", None))

        # ❌ If no staff → unauthorized
        if not hasattr(user, "staff") or not user.staff:
            return Response({"error": "No staff profile"}, status=403)

        role = user.staff.role   # ✅ CORRECT ROLE SOURCE

        # 🔵 Doctor → only their queue
        if role == "Doctor":
            appointments = Appointment.objects.filter(
                appointment_date=timezone.localdate(),
                status='Waiting',
                doctor__user=user
            )

        # 🟢 Receptionist → all queues
        elif role == "Receptionist":
            appointments = Appointment.objects.filter(
                appointment_date=timezone.localdate(),
                status='Waiting'
            )

        else:
            return Response({"error": "Unauthorized"}, status=403)

        appointments = appointments.select_related(
            'patient', 'doctor'
        ).prefetch_related('tokens')

        data = []

        for appt in appointments:
            token = appt.tokens.first()

            data.append({
                "appointment_id": appt.appointment_id,
                "patient_name": f"{appt.patient.first_name} {appt.patient.last_name or ''}",
                "doctor_name": f"{appt.doctor.user.first_name} {appt.doctor.user.last_name}",
                "token_number": token.token_number if token else None,
                "appointment_time": appt.appointment_time,
                "visit_type": appt.visit_type,
                "is_emergency": appt.is_emergency,
            })

        # ✅ Better sorting (emergency first)
        data = sorted(
            data,
            key=lambda x: (not x["is_emergency"], x["token_number"] or 999)
        )

        return Response(data)

class MarkNoShow(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        appointment = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("appointment")
        )

        appointment.status = "No Show"
        appointment.save()

        return Response({"message": "Marked as No Show"})


class CompleteConsultation(APIView):
    permission_classes = [IsDoctor]

    def post(self, request):
        appointment = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("appointment")
        )

        if appointment.status != "Waiting":
            return Response({"error": "Patient not in queue"})

        note = request.data.get("consultation_note")

        if not note:
            # return Response({"error": "Consultation note is required"})
            #  Default fallback 
          note = "Consultation completed without notes"

        appointment.status = "Completed"
        appointment.save()

        #  Create history with real doctor input
        PatientHistory.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            consultation_note=note
        )

        return Response({"message": "Consultation completed"})


class PatientHistoryView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request, patient_id):
        history = PatientHistory.objects.filter(patient_id=patient_id)

        serializer = PatientHistorySerializer(history, many=True)
        return Response(serializer.data)


# -------------------- LAB --------------------

class LabQueue(APIView):
    permission_classes = [IsLabTechnician]

    def get(self, request):
        return Response({"message": "Handled in lab module"})


# -------------------- BILLING --------------------

from decimal import Decimal

class CreateBill(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):

        appointment = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("appointment")
        )

        #  Prevent duplicate bill
        if Billing.objects.filter(appointment=appointment).exists():
            return Response({"error": "Bill already exists"})

        #  Only after consultation
        if appointment.status != "Completed":
            return Response({"error": "Consultation not completed"})

        consultation_fee = appointment.doctor.consultation_fee

        #  Lab cost (auto)
        lab_bill = getattr(appointment, 'lab_bill', None)
        lab_cost = lab_bill.total_amount if lab_bill else Decimal('0')

        # Pharmacy + Discount
        pharmacy_cost = Decimal(request.data.get("pharmacy_cost", 0))
        discount = Decimal(request.data.get("discount", 0))

        #  Basic validation
        if pharmacy_cost < 0 or discount < 0:
            return Response({"error": "Invalid cost values"})

        #  Prevent over-discount (IMPORTANT)
        total_before_discount = consultation_fee + lab_cost + pharmacy_cost
        if discount > total_before_discount:
            return Response({"error": "Discount exceeds total amount"})

        bill = Billing.objects.create(
            appointment=appointment,
            patient=appointment.patient,
            consultation_fee=consultation_fee,
            lab_cost=lab_cost,
            pharmacy_cost=pharmacy_cost,
            discount=discount,
            staff=getattr(request.user, 'staff', None)
        )

        #  Clean response 
        return Response({
            "bill_id": bill.bill_id,
            "consultation_fee": bill.consultation_fee,
            "lab_cost": bill.lab_cost,
            "pharmacy_cost": bill.pharmacy_cost,
            "discount": bill.discount,
            "total_amount": bill.total_amount,
            "payment_status": bill.payment_status
        })
class GetBill(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request, appointment_id):
        bill = get_object_or_404(
            Billing,
            appointment__appointment_id=appointment_id
        )

        serializer = BillingSerializer(bill)
        return Response(serializer.data)


class PayBill(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        bill = get_object_or_404(
            Billing,
            bill_id=request.data.get("bill_id")
        )

        #  Prevent double payment
        if bill.payment_status == "Paid":
            return Response({"error": "Bill already paid"})

        payment_method = request.data.get("payment_method")

        #  Validate payment method presence
        if not payment_method:
            return Response({"error": "Payment method required"})

        #  Validate allowed methods
        valid_methods = ["Cash", "Card", "UPI"]
        if payment_method not in valid_methods:
            return Response({"error": "Invalid payment method"})

        #  Update bill
        bill.payment_status = "Paid"
        bill.payment_method = payment_method
        bill.paid_at = timezone.now()
        bill.save()

        #  Clean response (professional)
        return Response({
            "bill_id": bill.bill_id,
            "payment_status": bill.payment_status,
            "payment_method": bill.payment_method
        })
#----------------bill generation-----------------






class GenerateBillPDF(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request, bill_id):

        bill = get_object_or_404(Billing, bill_id=bill_id)

        #  Dynamic data
        patient = bill.patient
        appointment = bill.appointment
        doctor = appointment.doctor
        staff = bill.staff

        doctor_name = f"{doctor.user.first_name} {doctor.user.last_name}"
        patient_name = f"{patient.first_name} {patient.last_name}"

        #  Response setup
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bill_{bill.bill_id}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # ---------------- HEADER ----------------
        elements.append(Paragraph("<b>Clinic Management System</b>", styles['Title']))
        elements.append(Paragraph("Consultation & Medical Services", styles['Normal']))
        elements.append(Spacer(1, 10))

        # ---------------- PATIENT DETAILS ----------------
        patient_data = [
            ["Name", patient_name, "Patient ID", patient.patient_code],
            ["Age", str(patient.age), "Bill No", str(bill.bill_id)],
            ["Doctor", doctor_name, "Visit Type", appointment.visit_type],
            ["Date", bill.created_at.strftime("%d-%m-%Y %I:%M %p"), "Payment", bill.payment_method or "Pending"],
            ["Status", bill.payment_status, "Generated By", str(staff) if staff else "System"]
        ]

        patient_table = Table(patient_data, colWidths=[80, 150, 80, 150])
        patient_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))

        elements.append(patient_table)
        elements.append(Spacer(1, 15))

        # ---------------- BILL ITEMS ----------------
        data = [
            ["Sl", "Item", "Rate", "Qty", "Amount"]
        ]

        row = 1

        # Consultation
        data.append([
            row, "Consultation Fee",
            str(bill.consultation_fee), 1,
            str(bill.consultation_fee)
        ])
        row += 1

        # Lab
        if bill.lab_cost > 0:
            data.append([
                row, "Lab Charges",
                str(bill.lab_cost), 1,
                str(bill.lab_cost)
            ])
            row += 1

        # Pharmacy
        if bill.pharmacy_cost > 0:
            data.append([
                row, "Pharmacy Charges",
                str(bill.pharmacy_cost), 1,
                str(bill.pharmacy_cost)
            ])
            row += 1

        table = Table(data, colWidths=[40, 200, 70, 50, 80])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

        # ---------------- TOTAL ----------------
        total_before = (
            Decimal(bill.consultation_fee) +
            Decimal(bill.lab_cost) +
            Decimal(bill.pharmacy_cost)
        )

        elements.append(Paragraph(
            f"Amount: ₹{total_before}    Discount: ₹{bill.discount}",
            styles['Normal']
        ))

        elements.append(Paragraph(
            f"<b>Total Payable: ₹{bill.total_amount}</b>",
            styles['Normal']
        ))

        elements.append(Spacer(1, 30))

        # ---------------- SIGNATURE ----------------
        elements.append(Paragraph("Authorized Signature", styles['Normal']))

        doc.build(elements)

        return response
    





class ReceptionDashboard(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request):

        #  Current date
        today = timezone.localdate()

        # ---------------- APPOINTMENT STATS ----------------
        total = Appointment.objects.filter(
            appointment_date=today
        ).count()

        completed = Appointment.objects.filter(
            appointment_date=today,
            status="Completed"
        ).count()

        pending = Appointment.objects.filter(
            appointment_date=today,
            status="Scheduled"
        ).count()

        # ---------------- REVENUE CALCULATION ----------------
        #  Use datetime range (real-world safe)
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)

        #  Revenue = only PAID bills
        revenue = Billing.objects.filter(
            paid_at__range=(start, end),
            payment_status__iexact="Paid"
        ).aggregate(
            total=Coalesce(Sum('total_amount'), Value(Decimal('0.00')))
        )['total']

        # ---------------- OPTIONAL (ADVANCED FEATURE) ----------------
        # Total generated bills (even unpaid)
        generated = Billing.objects.filter(
            created_at__date=today
        ).aggregate(
            total=Coalesce(Sum('total_amount'), Value(Decimal('0.00')))
        )['total']

        # ---------------- RESPONSE ----------------
        return Response({
            "date": today,
            "total_appointments": total,
            "completed": completed,
            "pending": pending,
            "revenue_collected": revenue,   #  actual money received
            "revenue_generated": generated  #  total bills generated
        })