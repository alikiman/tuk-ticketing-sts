from django import forms
from .models import Ticket, TicketResponse


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']


class TicketResponseForm(forms.ModelForm):

    class Meta:
        model = TicketResponse
        fields = ['message']