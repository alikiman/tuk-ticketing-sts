from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):
    # Added password fields to registration so students can actually set a password
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "class": "form-control"}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "class": "form-control"}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ("username", "email", "reg_no", "phone", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # UI improvements
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "e.g., John Kamau"
        })

        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "student@tukenya.ac.ke"
        })

        self.fields["reg_no"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "e.g., SCCI/01234/2024"
        })

        self.fields["phone"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "07XXXXXXXX"
        })

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # Force role for student
        user.role = "student"
        user.is_staff = False
        
        # CRITICAL: Hash the password properly!
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user

class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "role", "password")    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Securely hash the staff password
        user.set_password(self.cleaned_data["password"])
        
        # FIX THE UNIQUE CONSTRAINT FOR STAFF:
        # Generate a distinct staff placeholder using their unique username to bypass validation loops
        user.reg_no = f"STAFF/{user.username.upper().replace(' ', '')}"

        # Automatically make staff users active team members
        if user.role == "staff":
            user.is_staff = True

        if commit:
            user.save()
        return user