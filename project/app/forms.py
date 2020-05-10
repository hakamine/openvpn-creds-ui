from django import forms


class PKIPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(),
                               min_length=8, max_length=32)

    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # check that password is alphanumeric
        if not password.isalnum():
            raise forms.ValidationError(
                "password should contain alphanumeric characters only"
            )

        # check that password contains only lowercase,uppercase, and digits

        if password != confirm_password:
            raise forms.ValidationError(
                "passwords do not match"
            )
