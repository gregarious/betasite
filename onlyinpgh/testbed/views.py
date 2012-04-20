from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.core.urlresolvers import reverse


def home(request):
    return render(request, 'testbed/home.html')
