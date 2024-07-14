from django.shortcuts import render
from django.http import HttpResponse # importe o HttpResponse 

# Create your views here.

def index(req):
    return HttpResponse("Hello !")
