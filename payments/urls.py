from django.urls import path
from .views import LoanScheduleView, ModifyPaymentView

urlpatterns = [
    path("loan-schedule/", LoanScheduleView.as_view(), name="loan-schedule"),
    path(
        "modify-payment/<int:payment_id>/",
        ModifyPaymentView.as_view(),
        name="modify-payment",
    ),
]
