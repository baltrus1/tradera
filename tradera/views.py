from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .job import Job

### Currently Job is singleton, ideally with each request new Job could be created, in request 
#   a string symbol should be passed for which currencies to follow(eg. "dogebtc"), a number for how many last trades 
#   should be considered. This api could return job id, which could then be looked up when stopping job, 
#   also /list api could be added to list all running jobs.
def start_job(request):
    message = Job.get().start()
    return HttpResponse(message)

def stop_job(request):
    message = Job.get().stop()
    return HttpResponse(message)
    
def get_prices(request):
    data = {'max': Job.get().get_max_price(), 'min': Job.get().get_min_price()}

    return JsonResponse(data, safe=False)
