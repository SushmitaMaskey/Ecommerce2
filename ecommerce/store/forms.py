from django.forms.forms import Form
from .models import Order, Customer, Product
from django.contrib.auth.models import User
from django import forms

class CheckoutForm(forms.ModelForm):
    class Meta:
        model= Order
        fields= ['ordered_by', 'shipping_address', 'mobile', 'email', 'payment_method']

class CustomerRegistrationForm(forms.ModelForm):
    username= forms.CharField(widget=forms.TextInput()) 
    password=forms.CharField(widget=forms.PasswordInput())
    email=forms.CharField(widget=forms.EmailInput())
    
    class Meta:
        model= Customer
        fields=['username','password','email','full_name', 'address']

    def clean_username(self):
        uname=self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError('Username already exists')
        
        return uname

class CustomerLoginForm(forms.Form):
    username= forms.CharField(widget=forms.TextInput()) 
    password=forms.CharField(widget=forms.PasswordInput())

class AdminProductCreateForm(forms.ModelForm):
    more_images=forms.FileField(required=False, widget= forms.FileInput(attrs={
        'class':'form-control',
        'multiple': True
    }))

    class Meta: #automatically saves
        model= Product
        fields=['title', 'slug', 'category', 'image', 'description','marked_price', 'selling_price', 'warranty', 
                'return_policy']
        widgets= {
            'title': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder': 'Enter title here...'
            }),
            'slug': forms.TextInput(attrs={
                'class':'form-control',
                'placeholder': 'Enter slug here...'
            }),
            'category': forms.Select(attrs={
                'class':'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class':'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class':'form-control',
                'placeholder': 'Enter description here...',
                'rows': 4
            }),
            'marked_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter marked price here...'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter Selling Price here...'
            }),
            'warranty': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter warranty here...'
            }),
            'return_policy': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'enter return policy here...'
            })
        }
class PasswordResetForm(forms.Form):
    email= forms.CharField(widget= forms.EmailInput(attrs={
         'class': 'form-control',
         'placeholder': 'Enter you email here'
     }))
    
    def clean_email(self):
        e= self.cleaned_data.get('email')
        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError('Email Error!')
        return e
             

class PasswordChangeForm(forms.Form):
    new_password= forms.CharField(widget= forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder': 'Enter new password',
        'autocomplete': 'new-password'
        }), label='New Password')

    confirm_new_password= forms.CharField(widget= forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder': 'Confirm new password',
        'autocomplete': 'new-password'
        }), label='Confirm New Password')

    def clean_confirm_new_password(self):
        new_password= self.cleaned_data.get('new_password')
        confirm_new_password= self.cleaned_data.get('confirm_new_password')
        if new_password!=confirm_new_password:
            raise forms.ValidationError('Passwords do not match!')

        return confirm_new_password