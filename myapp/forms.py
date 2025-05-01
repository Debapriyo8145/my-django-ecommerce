from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,  Review

class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser 
        fields = ['username','first_name','last_name', 'email', 'mobile']
        

class ChangeForm(UserChangeForm):
    password = None  

    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={'class': 'form-control border-primary'})
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={'class': 'form-control border-primary'})
    )
    email = forms.EmailField(  # ✅ Better to use EmailField for email validation
        label="Email-ID",
        widget=forms.EmailInput(attrs={'class': 'form-control border-primary'})
    )
    mobile = forms.CharField(
        label="Contact Number",
        widget=forms.TextInput(attrs={'class': 'form-control border-primary'})  # NumberInput is for numeric-only input, but CharField is okay here
    )
    profile_image = forms.ImageField(
        label="Profile Image",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control border-primary'})
    )
    class Meta:
        model = CustomUser 
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile', 'profile_image']
  
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'review', 'rating']