from django import forms
from .models import Cultivator




class CultivatorForm(forms.Form):

    cultivator_list = []
    cultivators = Cultivator.objects.all().order_by('name')

    for cultivator in cultivators:
        cultivator_list.append((cultivator.id, cultivator.name))

    CULTIVATOR_CHOICES = tuple(cultivator_list)

    cultivator_id = forms.ChoiceField(choices=CULTIVATOR_CHOICES)