from django import forms
from django.contrib.auth.models import User
from .models import GuestProfile
from reviews.models import Review


class GuestRegistrationForm(forms.ModelForm):

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput()
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email'
        ]

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class ProfilePictureForm(forms.ModelForm):

    class Meta:
        model = GuestProfile
        fields = ['profile_picture']


class GuestReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = [
            'rating',
            'comment'
        ]