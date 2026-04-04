from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from datetime import date, time

from administration.models import Doctor, Department
from reception.models import Patient, Appointment


class ReceptionistAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -------------------- GROUPS --------------------
        Group.objects.create(name="receptionist")
        Group.objects.create(name="doctor")

        # -------------------- USERS --------------------
        self.receptionist_user = User.objects.create_user(
            username="reception",
            password="Test@123"
        )
        self.receptionist_user.groups.add(Group.objects.get(name="receptionist"))

        self.doctor_user = User.objects.create_user(
            username="doctor",
            password="Test@123"
        )
        self.doctor_user.groups.add(Group.objects.get(name="doctor"))

        # -------------------- LOGIN (JWT) --------------------
        login_response = self.client.post('/api/auth/login/', {
            "username": "reception",
            "password": "Test@123"
        })

        self.token = login_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # -------------------- DEPARTMENT --------------------
        self.department = Department.objects.create(
            dept_code="CARD",
            dept_name="Cardiology"
        )

        # -------------------- DOCTOR --------------------
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            department=self.department,
            date_of_birth=date(1990, 1, 1),
            qualification="MBBS",
            experience_years=5,
            license_number="LIC123",
            consultation_fee=500,
            phone_number="1234567890"
        )

    # -------------------- PATIENT --------------------

    def test_register_patient(self):
        response = self.client.post('/api/v1/patients/', {
            "phone_number": "9999999999",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "blood_group": "A+",
            "address": "Test Address"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("patient_code", response.data)

    def test_invalid_patient(self):
        response = self.client.post('/api/v1/patients/', {
            "phone_number": "123"  # invalid
        })
        self.assertEqual(response.status_code, 400)

    def test_search_patient(self):
        Patient.objects.create(
            phone_number="8888888888",
            first_name="Alice",
            last_name="Test",
            date_of_birth="2000-01-01",
            gender="Female",
            blood_group="B+",
            address="Test"
        )

        response = self.client.get('/api/v1/patients/search/?q=Ali')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

    # -------------------- APPOINTMENT --------------------

    def test_create_appointment(self):
        patient = Patient.objects.create(
            phone_number="7777777777",
            first_name="Bob",
            last_name="Test",
            date_of_birth="2000-01-01",
            gender="Male",
            blood_group="O+",
            address="Test"
        )

        response = self.client.post('/api/v1/appointments/', {
            "patient": patient.patient_id,
            "doctor": self.doctor.doctor_id,
            "appointment_date": str(date.today()),
            "appointment_time": "10:00:00",
            "visit_type": "New"
        })

        self.assertEqual(response.status_code, 200)

    def test_double_booking(self):
        patient = Patient.objects.create(
            phone_number="6666666666",
            first_name="Test",
            last_name="User",
            date_of_birth="2000-01-01",
            gender="Male",
            blood_group="O+",
            address="Test"
        )

        Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            visit_type="New"
        )

        response = self.client.post('/api/v1/appointments/', {
            "patient": patient.patient_id,
            "doctor": self.doctor.doctor_id,
            "appointment_date": str(date.today()),
            "appointment_time": "10:00:00",
            "visit_type": "New"
        })

        self.assertEqual(response.status_code, 400)

    # -------------------- TOKEN --------------------

    def test_generate_token(self):
        patient = Patient.objects.create(
            phone_number="5555555555",
            first_name="Token",
            last_name="User",
            date_of_birth="2000-01-01",
            gender="Male",
            blood_group="O+",
            address="Test"
        )

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            appointment_date=date.today(),
            appointment_time=time(11, 0),
            visit_type="New"
        )

        response = self.client.post('/api/v1/tokens/', {
            "appointment": appointment.appointment_id
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("token_number", response.data)

    # -------------------- WALK-IN --------------------

    def test_walkin(self):
        response = self.client.post('/api/v1/walkin/', {
            "phone_number": "4444444444",
            "first_name": "Walk",
            "last_name": "In",
            "date_of_birth": "2000-01-01",
            "gender": "Male",
            "blood_group": "O+",
            "address": "Test",
            "doctor": self.doctor.doctor_id
        })

        self.assertEqual(response.status_code, 200)

    # -------------------- BILLING --------------------

    def test_create_and_pay_bill(self):
        patient = Patient.objects.create(
            phone_number="3333333333",
            first_name="Bill",
            last_name="User",
            date_of_birth="2000-01-01",
            gender="Male",
            blood_group="O+",
            address="Test"
        )

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=self.doctor,
            appointment_date=date.today(),
            appointment_time=time(12, 0),
            visit_type="New"
        )

        # Create Bill
        bill_response = self.client.post('/api/v1/billing/create/', {
            "appointment": appointment.appointment_id
        })

        self.assertEqual(bill_response.status_code, 200)

        bill_id = bill_response.data.get("bill_id")

        # Pay Bill
        pay_response = self.client.post('/api/v1/billing/pay/', {
            "bill_id": bill_id,
            "payment_method": "Cash"
        })

        self.assertEqual(pay_response.status_code, 200)

    # -------------------- PERMISSION --------------------

    def test_permission_denied(self):
        user = User.objects.create_user(username="normal", password="123")
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/v1/patients/')
        self.assertEqual(response.status_code, 403)