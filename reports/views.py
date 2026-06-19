from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from tickets.models import Ticket
from .models import ReportLog


# =========================
# LIST REPORTS
# =========================
@login_required
def report_list(request):

    reports = ReportLog.objects.all().order_by("-generated_at")

    return render(request, "reports/report_list.html", {
        "reports": reports
    })


# =========================
# GENERATE REPORT
# =========================
@login_required
def generate_report(request):

    if request.user.role not in ["admin", "staff"]:
        return redirect("dashboard_redirect")

    total = Ticket.objects.count()
    open_t = Ticket.objects.filter(status="open").count()
    closed_t = Ticket.objects.filter(status="closed").count()

    ReportLog.objects.create(
        report_name="System Ticket Report",
        generated_by=request.user,
        total_tickets=total,
        open_tickets=open_t,
        closed_tickets=closed_t
    )

    return redirect("report-list")