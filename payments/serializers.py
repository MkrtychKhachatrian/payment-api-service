from rest_framework import serializers
from .models import Loan, PaymentSchedule


class LoanSerializer(serializers.ModelSerializer):
    loan_start_date = serializers.DateField(input_formats=["%d-%m-%Y"])

    class Meta:
        model = Loan
        fields = [
            "amount",
            "loan_start_date",
            "number_of_payments",
            "periodicity",
            "interest_rate",
        ]


class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = ["id", "date", "principal", "interest", "remaining_balance"]
