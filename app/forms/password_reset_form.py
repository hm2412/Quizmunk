from django import forms
from django.contrib.auth.password_validation import validate_password

class PasswordResetForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Current Password",
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="New Password",
        validators=[validate_password],  # Ensures strong password rules
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm New Password",
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Incorrect current password.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data
