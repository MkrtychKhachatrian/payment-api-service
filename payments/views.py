from datetime import datetime
from decimal import Decimal, InvalidOperation

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PaymentSchedule
from .serializers import LoanSerializer
from django.shortcuts import get_object_or_404

from .utils import (
    generate_payment_schedule,
    update_subsequent_payments,
    handle_loan_creation,
)


class LoanScheduleView(APIView):
    """
    API view for creating a loan and generating its payment schedule.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a loan and generate the payment schedule.

        Args:
            request (Request): The HTTP request object containing the loan data.

        Returns:
            Response: A Response object containing the payment schedule if successful, or error details if the request is invalid.
        """
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            loan = handle_loan_creation(serializer.validated_data)
            # Generate payment schedule
            schedule = generate_payment_schedule(
                principal=loan.amount,
                annual_interest_rate=loan.interest_rate,
                periods=loan.number_of_payments,
                start_date=datetime.combine(loan.loan_start_date, datetime.min.time()),
                periodicity=loan.periodicity,
            )
            return Response(schedule, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModifyPaymentView(APIView):
    """
    API view for modifying an existing payment's principal amount.
    """

    def patch(self, request, payment_id):
        """
        Handle PATCH requests to update the principal amount of a specific payment.

        Args:
            request (Request): The HTTP request object containing the new principal amount.
            payment_id (int): The ID of the payment to be modified.

        Returns:
            Response: A Response object indicating the result of the modification. Returns error details if the principal amount is invalid.
        """
        payment = get_object_or_404(PaymentSchedule, id=payment_id)
        new_principal = request.data.get("principal", None)

        if new_principal is not None:
            try:
                new_principal = Decimal(new_principal)
            except (ValueError, InvalidOperation):
                return Response({"error": "Invalid principal amount"}, status=400)

            # Update the principal amount
            old_principal = payment.principal
            payment.principal = new_principal

            # Recalculate the remaining balance and interest for this payment
            remaining_balance = (
                payment.remaining_balance + old_principal - new_principal
            )
            payment.remaining_balance = remaining_balance
            payment.interest = remaining_balance * (
                payment.loan.interest_rate / 12
            )  # Update interest
            payment.save()

            # Recalculate interest for subsequent payments
            update_subsequent_payments(payment.loan)

            return Response({"status": "Payment modified", "payment_id": payment.id})

        return Response({"error": "Invalid principal amount"}, status=400)
