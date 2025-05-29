from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser,OtpCode


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('first_name','last_name', 'phone_number')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match")
        return cd['password2']

    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='you cant change password using <a href="../password/">this form</a>.')

    class Meta:
        model = CustomUser

        fields = ('first_name','last_name', 'phone_number', 'password','last_login')

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ('first_name', 'last_name', 'phone_number', 'birthday', 'password1', 'password2','referraler_code')
#
#     referraler_code='referraler_code'
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # Set custom labels for fields
#         self.fields['first_name'].label = 'نام'
#         self.fields['last_name'].label = 'نام خانوادگی'
#         self.fields['phone_number'].label = 'شماره موبایل'
#         self.fields['birthday'].label = 'تاریخ تولد'
#         self.fields['password1'].label = 'رمز عبور'
#         self.fields['password2'].label = 'تکرار رمز عبور'
#         self.fields['referraler_code'].label = 'کد معرف (اختیاری)'
#
# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ('phone_number', 'first_name', 'last_name')
#
# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ['first_name', 'last_name',]



#      register

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = CustomUser.objects.filter(phone_number=phone_number).exists()
        if user:
            raise ValidationError('این شماره قبلاً ثبت شده است.')
        OtpCode.objects.filter(phone_number=phone_number).delete()
        return phone_number



class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()



#      login

class PhoneLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=11)


class OTPVerifyForm(forms.Form):
    code = forms.IntegerField()



#  profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
                'placeholder': 'نام'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input block w-full mt-1 rounded-md border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
                'placeholder': 'نام خانوادگی'
            }),
        }
