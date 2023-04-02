from django import forms
from .models import Crop



class HarvestForm(forms.Form):

    crops = Crop.objects.all().order_by('-date_created')
    crop_choices_list = [('------', '------')]

    for crop in crops:
        crop_choices_list.append((crop.id, crop.__str__()))

    CROP_CHOICES = tuple(crop_choices_list)

    crop        = forms.ChoiceField(choices=CROP_CHOICES)
    yield_dry   = forms.IntegerField()
    bag_count   = forms.IntegerField(initial=1)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['yield_dry'].widget.attrs = {'placeholder' : 'Yield dry (g)'}