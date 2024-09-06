from django.db import models


class Loan(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_start_date = models.DateField()
    number_of_payments = models.IntegerField()
    periodicity = models.CharField(max_length=2)  # e.g., '1m', '6m'
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Loan of {self.amount} with {self.number_of_payments} payments"


class PaymentSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField()
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment on {self.date} - Principal: {self.principal}, Interest: {self.interest}"
