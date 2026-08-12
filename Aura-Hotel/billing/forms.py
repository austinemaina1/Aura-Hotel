from django import forms
from .models import InvoiceItem


class InvoiceItemForm(forms.ModelForm):

    class Meta:
        model = InvoiceItem

        fields = [
            'description',
            'quantity',
            'unit_price'
        ]

        widgets = {

            'description': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'unit_price': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }