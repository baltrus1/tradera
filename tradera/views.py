from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from .job import Job

### Currently Job is singleton, ideally with each request new Job could be created, in request 
#   a string should be passed for which currencies to follow(eg. "dogebtc", a number for how many last trades 
#   should be considered. This api could return job id, which could then be looked up when stopping job, 
#   also /list api could be added to list all running jobs.
def startJob(request):
    message = Job.get().start()
    return HttpResponse(message)

def stopJob(request):
    message = Job.get().stop()
    return HttpResponse(message)
    
def getPrices(request):
    data = {'maxPrice': Job.get().getMaxPrice(), 'minPrice': Job.get().getMinPrice()}

    return JsonResponse(data, safe=False)
