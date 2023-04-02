from http.client import HTTPResponse
from django.shortcuts import render, get_object_or_404, redirect
from .classes import FreezerBag
from .forms import HarvestForm
from .models import Monotub, Flush, Crop
from .serializers import RecipeSerializer, MonotubSerializer
from django.http import JsonResponse
from django.db.models import Sum

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView



from datetime import datetime, timedelta
import decimal


# @api_view(['GET'])
# def get_data(request):


class GetDataView(APIView):

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(request, *args, **kwargs):

        monotubs = Monotub.objects.all()
        serializer = MonotubSerializer(monotubs, many=True)

        return Response(serializer.data)




class AddDataView(APIView):

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def post(request, *args, **kwargs):

        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)

        return Response(serializer.data)


def monotub_whatever(request):

    monotubs = Monotub.objects.all()

    serializer = MonotubSerializer(monotubs, many=True)
    print(serializer)

    return JsonResponse(serializer.data, safe=False)



def crop(request):

    time_thresh = datetime.now() - timedelta(days=20)
    flushes = Flush.objects.filter(date_harvested__gt=time_thresh)

    total_yield_wet = flushes.aggregate(Sum('yield_wet'))
    try:
        yield_estimate = round(total_yield_wet['yield_wet__sum'] * decimal.Decimal(0.1), 2) 
    except TypeError:
        yield_estimate = 0
    yield_estimate_oz = round(yield_estimate / 28, 2)
    yield_estimate_lb = round(yield_estimate_oz / 16, 2)

    crop = Crop.objects.all().first()
    crop.actual_vs_estimate()

    print(crop.start_date())
    print(crop.end_date())

    context = {
        'flushes'           : flushes,
        'yield_estimate'    : yield_estimate,
        'yield_estimate_oz' : yield_estimate_oz,
        'yield_estimate_lb' : yield_estimate_lb,
    }

    return render(request, 'crop.html', context)



def harvest_form(request):

    if request.method == 'POST':
        harvest_form = HarvestForm(request.POST)
        
        if harvest_form.is_valid():
            crop_id     = harvest_form.cleaned_data['crop']
            yield_dry   = harvest_form.cleaned_data['yield_dry']
            bag_count   = harvest_form.cleaned_data['bag_count']

            crop        = get_object_or_404(Crop, id=crop_id)
            freezer_bag = FreezerBag(bag_weight=13.5, silica_packs=2)

            if crop.yield_dry == 0:
                crop.yield_dry = yield_dry - freezer_bag.weight * bag_count
                crop.save()
            else:
                print('....break')
                return redirect('harvest_form')

    harvest_form = HarvestForm()

    context = {
        'harvest_form' : harvest_form,
    }

    return render(request, 'cultivation/harvest_form.html', context)