from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.report_list, name="report-list"),
    path("generate/", views.generate_report, name="generate-report"),
]