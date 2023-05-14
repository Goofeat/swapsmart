from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from SwapSmart.models import Ad


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='First name', max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last name', max_length=30, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        elif not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        elif not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        elif not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        return password


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ('image', 'title', 'category', 'description', 'condition', 'price', 'phone')
        labels = {
            'image': 'Image',
            'title': 'Title',
            'category': 'Category',
            'description': 'Description',
            'condition': 'Condition',
            'price': 'Price',
            'phone': 'Phone',
        }
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirm new password",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    error_messages = {
        **PasswordChangeForm.error_messages,
        'password_incorrect': "Your current password was entered incorrectly.",
        'password_mismatch': "The two password fields didn't match.",
        'password_common': "This password is too common.",
        'password_short': "Password must be at least 8 characters.",
        'password_numeric': "This password is entirely numeric.",
        'password_entirely_alphabetic': "This password is entirely alphabetic."
    }

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        password_validation.validate_password(password, self.user)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if 'new_password1' in cleaned_data and 'new_password2' in cleaned_data:
            if cleaned_data['new_password1'] != cleaned_data['new_password2']:
                self.add_error('new_password2', self.error_messages['password_mismatch'])
        return cleaned_data

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
