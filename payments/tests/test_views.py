from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal
from payments.models import Loan, PaymentSchedule


class LoanScheduleTests(APITestCase):
    def setUp(self):
        self.create_loan_url = reverse("loan-schedule")

    def test_create_loan_and_schedule(self):
        data = {
            "amount": "10000",
            "loan_start_date": "01-09-2024",  # Updated date format to DD-MM-YYYY
            "number_of_payments": 12,
            "periodicity": "1m",
            "interest_rate": "5.0",
        }
        response = self.client.post(self.create_loan_url, data, format="json")
        print(response.data)  # Print response content to debug
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(PaymentSchedule.objects.count(), 12)

    def test_create_loan_invalid_data(self):
        data = {
            "amount": "10000",
            "loan_start_date": "invalid-date",
            "number_of_payments": 12,
            "periodicity": "1m",
            "interest_rate": "5.0",
        }
        response = self.client.post(self.create_loan_url, data, format="json")
        print(response.data)  # Print response content to debug
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ModifyPaymentTests(APITestCase):
    def setUp(self):
        self.create_loan_url = reverse("loan-schedule")
        self.modify_payment_url = None  # Initialize to None

        # Create a loan and schedule for testing
        data = {
            "amount": "10000",
            "loan_start_date": "01-09-2024",  # Updated date format to DD-MM-YYYY
            "number_of_payments": 12,
            "periodicity": "1m",
            "interest_rate": "5.0",
        }
        self.client.post(self.create_loan_url, data, format="json")

        # Get the first payment for modification
        self.payment = PaymentSchedule.objects.first()
        if self.payment:
            self.modify_payment_url = reverse("modify-payment", args=[self.payment.id])
        else:
            self.fail("Payment was not created.")

    def test_modify_payment(self):
        if self.modify_payment_url:
            data = {"principal": "500"}
            response = self.client.patch(self.modify_payment_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.payment.refresh_from_db()
            self.assertEqual(self.payment.principal, Decimal("500"))
        else:
            self.fail("Modify payment URL is not set.")

    def test_modify_payment_invalid_amount(self):
        if self.modify_payment_url:
            data = {"principal": "invalid"}
            response = self.client.patch(self.modify_payment_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            self.fail("Modify payment URL is not set.")
