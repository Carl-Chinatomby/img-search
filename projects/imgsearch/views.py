# Create your views here.

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response
from django import forms
from django.db import models

class UploadFile(forms.Form):
    name = models.ImageField()
    

def handle_file_upload(f):

    return

def main(request):
    
    t = loader.get_template("main/index.html")
    return render_to_response('main/index.html', context_instance=RequestContext(request))



def upload(request):
    
    
    return render_to_response('upload/index.html', context_instance=RequestContext(request))


def results(request):

    c = Context({})
    t = loader.get_template('results/index.html')
    return HttpResponse(t.render(c))

def upload_file(request):

    if request.method == "POST":
        form = UploadFile(request.POST, request.FILES['file']);
        
    return render_to_response("upload/complete.html", context_instance=RequestContext(request))
    
