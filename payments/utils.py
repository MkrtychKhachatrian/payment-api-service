from datetime import timedelta, datetime
from decimal import Decimal

from payments.models import PaymentSchedule, Loan


def calculate_emi(principal, annual_interest_rate, periods, length_of_period_fraction):
    """
    Calculate the Equated Monthly Installment (EMI) for a loan.

    Args:
        principal (float or Decimal): The loan principal amount.
        annual_interest_rate (float or Decimal): The annual interest rate (as a percentage).
        periods (int): The number of payment periods.
        length_of_period_fraction (float or Decimal): The fraction of the year for each period.

    Returns:
        Decimal: The EMI amount.
    """
    principal = Decimal(principal)
    annual_interest_rate = Decimal(annual_interest_rate)
    length_of_period_fraction = Decimal(length_of_period_fraction)

    i = annual_interest_rate * length_of_period_fraction  # interest rate per period
    emi = i * principal / (1 - (1 + i) ** -periods)
    return emi


def generate_payment_schedule(
    principal, annual_interest_rate, periods, start_date, periodicity
):
    """
    Generate a payment schedule based on the loan details.

    Args:
        principal (float or Decimal): The loan principal amount.
        annual_interest_rate (float or Decimal): The annual interest rate (as a percentage).
        periods (int): The number of payment periods.
        start_date (datetime): The start date of the loan.
        periodicity (str): The payment periodicity, e.g., '1m', '2w', '30d'.

    Returns:
        list of dict: A list of payment schedule entries, each containing 'id', 'date', 'principal',
                      'interest', and 'remaining_balance'.
    """
    length_of_period_fraction = get_period_fraction(periodicity)
    emi = calculate_emi(
        principal, annual_interest_rate, periods, length_of_period_fraction
    )
    schedule = []
    remaining_principal = Decimal(principal)

    for payment_num in range(1, periods + 1):
        interest = remaining_principal * (
            annual_interest_rate * length_of_period_fraction
        )
        principal_payment = emi - interest
        remaining_principal -= principal_payment

        payment_date = get_next_payment_date(start_date, periodicity, payment_num)

        schedule.append(
            {
                "id": payment_num,
                "date": payment_date.strftime("%Y-%m-%d"),
                "principal": round(principal_payment, 2),
                "interest": round(interest, 2),
                "remaining_balance": round(remaining_principal, 2),
            }
        )

    return schedule


def get_period_fraction(periodicity):
    """
    Convert the periodicity string into a fraction of a year.

    Args:
        periodicity (str): The payment periodicity, e.g., '1m', '2w', '30d'.

    Returns:
        Decimal: The fraction of the year for the specified periodicity.
    """
    if periodicity.endswith("m"):
        return Decimal(int(periodicity[:-1])) / Decimal(12)
    elif periodicity.endswith("w"):
        return Decimal(int(periodicity[:-1])) / Decimal(52)
    elif periodicity.endswith("d"):
        return Decimal(int(periodicity[:-1])) / Decimal(365)


def get_next_payment_date(start_date, periodicity, payment_num):
    """
    Calculate the date of the next payment based on the periodicity.

    Args:
        start_date (datetime): The start date of the loan.
        periodicity (str): The payment periodicity, e.g., '1m', '2w', '30d'.
        payment_num (int): The payment number.

    Returns:
        datetime: The date of the next payment.
    """
    if periodicity.endswith("m"):
        return start_date + timedelta(days=30 * int(periodicity[:-1]) * payment_num)
    elif periodicity.endswith("w"):
        return start_date + timedelta(weeks=int(periodicity[:-1]) * payment_num)
    elif periodicity.endswith("d"):
        return start_date + timedelta(days=int(periodicity[:-1]) * payment_num)


def update_subsequent_payments(loan):
    """
    Update interest for subsequent payments of a loan after modifying one payment.

    Args:
        loan (Loan): The loan object for which payments need to be updated.

    Returns:
        None
    """
    payments = PaymentSchedule.objects.filter(loan=loan).order_by("date")

    for i in range(len(payments)):
        payment = payments[i]
        if i == 0:
            continue

        if i == 1:
            previous_payment = payments[i - 1]
            remaining_balance = previous_payment.remaining_balance
        else:
            previous_payment = payments[i - 1]
            remaining_balance = previous_payment.remaining_balance

        payment.interest = remaining_balance * (loan.interest_rate / 12)
        payment.save()


def handle_loan_creation(validated_data):
    """
    Create a loan and generate the associated payment schedule based on validated data.

    Args:
        validated_data (dict): The validated data for the loan, including amount, loan_start_date,
                               number_of_payments, periodicity, and interest_rate.

    Returns:
        Loan: The created Loan object.
    """
    loan = Loan.objects.create(**validated_data)
    start_date = datetime.combine(
        validated_data["loan_start_date"], datetime.min.time()
    )
    schedule = generate_payment_schedule(
        principal=loan.amount,
        annual_interest_rate=loan.interest_rate,
        periods=loan.number_of_payments,
        start_date=start_date,
        periodicity=loan.periodicity,
    )
    for payment in schedule:
        PaymentSchedule.objects.create(
            loan=loan,
            date=payment["date"],
            principal=payment["principal"],
            interest=payment["interest"],
            remaining_balance=payment["remaining_balance"],
        )
    return loan
