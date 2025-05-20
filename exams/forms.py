from django import forms
from django.core.exceptions import ValidationError
from .models import ExamRegistration


class ExamRegistrationForm(forms.ModelForm):
    """Form for registering for an exam"""
    
    class Meta:
        model = ExamRegistration
        fields = ['payment_image']
        labels = {
            'payment_image': 'تصویر فیش پرداخت',
        }
        widgets = {
            'payment_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def clean_card_number(self):
        """Validate card number to be numeric and exactly 16 digits"""
        card_number = self.cleaned_data.get('card_number')
        
        if not card_number.isdigit():
            raise ValidationError('شماره کارت باید فقط شامل اعداد باشد.')
        
        if len(card_number) != 16:
            raise ValidationError('شماره کارت باید 16 رقم باشد.')
        
        return card_number 