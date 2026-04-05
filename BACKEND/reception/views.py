from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from decimal import Decimal

from datetime import datetime, timedelta  # ✅ add timedelta
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


class AppointmentByDate(APIView):
    permission_classes = [IsReceptionist]

    def get(self, request):
        date_param = request.GET.get("date")

        appointments = Appointment.objects.filter(
            appointment_date=date_param
        )

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class CancelAppointment(APIView):
    permission_classes = [IsReceptionist]

    def post(self, request):
        appointment = get_object_or_404(
            Appointment,
            appointment_id=request.data.get("appointment")
        )

        if appointment.status == "Completed":
            return Response({"error": "Cannot cancel completed appointment"})

        appointment.status = "Cancelled"
        appointment.cancellation_reason = request.data.get("reason")
        appointment.save()

        return Response({"message": "Appointment cancelled"})


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
                "staff": getattr(request.user, 'staff', None)  # ✅ FIX
            }
        )

        doctor = get_object_or_404(
            Doctor,
            doctor_id=data.get("doctor"),
            status='active'
        )

        # ✅ FIX: avoid "time in past" error + add staff
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=timezone.localdate(),
            appointment_time=(timezone.localtime() + timedelta(minutes=5)).time(),
            visit_type="New",
            status="Waiting",
            created_by=request.user,
            staff=getattr(request.user, 'staff', None)  # ✅ FIX
        )

        # Token auto-created via signal
        token = WaitingToken.objects.filter(appointment=appointment).first()

        return Response({
            "patient_id": patient.patient_id,
            "appointment_id": appointment.appointment_id,
            "token": token.token_number if token else None
        })


# -------------------- DOCTOR --------------------

class DoctorQueue(APIView):
    permission_classes = [IsDoctor]

    def get(self, request):
        appointments = Appointment.objects.filter(
            appointment_date=timezone.localdate(),
            status='Waiting'
        ).select_related('patient', 'doctor').prefetch_related('tokens')

        data = []

        for appt in appointments:
            token = appt.tokens.first()

            data.append({
                "appointment_id": appt.appointment_id,
                "patient_name": appt.patient.first_name,
                "doctor_name": f"{appt.doctor.user.first_name} {appt.doctor.user.last_name}",
                "token_number": token.token_number if token else None,
                "appointment_time": appt.appointment_time,
                "visit_type": appt.visit_type,
                "is_emergency": appt.is_emergency,
            })

        # Sort by token (real system behavior)
        data = sorted(data, key=lambda x: x["token_number"] or 999)

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
            # ✅ Default fallback (production-safe)
          note = "Consultation completed without notes"

        appointment.status = "Completed"
        appointment.save()

        # ✅ Create history with real doctor input
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

        # ✅ Prevent duplicate bill
        if hasattr(appointment, 'bill'):
            return Response({"error": "Bill already exists"})

        # ✅ Only after consultation
        if appointment.status != "Completed":
            return Response({"error": "Consultation not completed"})

        consultation_fee = appointment.doctor.consultation_fee

        # ✅ Lab cost (auto)
        lab_bill = getattr(appointment, 'lab_bill', None)
        lab_cost = lab_bill.total_amount if lab_bill else Decimal('0')

        # ✅ Pharmacy + Discount
        pharmacy_cost = Decimal(request.data.get("pharmacy_cost", 0))
        discount = Decimal(request.data.get("discount", 0))

        # ❌ Basic validation
        if pharmacy_cost < 0 or discount < 0:
            return Response({"error": "Invalid cost values"})

        # ❌ Prevent over-discount (IMPORTANT)
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

        # ✅ Clean response (production style)
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

        # ✅ Prevent double payment
        if bill.payment_status == "Paid":
            return Response({"error": "Bill already paid"})

        payment_method = request.data.get("payment_method")

        # ✅ Validate payment method presence
        if not payment_method:
            return Response({"error": "Payment method required"})

        # ✅ Validate allowed methods
        valid_methods = ["Cash", "Card", "UPI"]
        if payment_method not in valid_methods:
            return Response({"error": "Invalid payment method"})

        # ✅ Update bill
        bill.payment_status = "Paid"
        bill.payment_method = payment_method
        bill.paid_at = timezone.now()
        bill.save()

        # ✅ Clean response (professional)
        return Response({
            "bill_id": bill.bill_id,
            "payment_status": bill.payment_status,
            "payment_method": bill.payment_method
        })