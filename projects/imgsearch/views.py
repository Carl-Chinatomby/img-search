# Create your views here.

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response
from django import forms
from django.db import models

import StringIO

#This needs to point to your repository static/image folder!
IMAGE_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/images'

#This needs to point to your repository static/videos folder!
VIDEO_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/videos'


class UploadFile(forms.Form):
    name = models.ImageField()
    

def handle_img_upload(f):
   
    
    print IMAGE_DIR + '/' + f.name
    try:    
        o = open(IMAGE_DIR + '/' + f.name, "wb")
        
        
    except IOError:
        print "Error opening file for writing!"
        exit(-1)

    f.open()
    for chunk in f.chunks():
        o.write(chunk)
    
    f.close()
    o.close()

    return

def handle_img_search(f):
   
    """
    print IMAGE_DIR + '/' + f.name
    try:    
        o = open(IMAGE_DIR + '/' + f.name, "wb")
        
        
    except IOError:
        print "Error opening file for writing!"
        exit(-1)

    f.open()
    for chunk in f.chunks():
        o.write(chunk)
    
    f.close()
    o.close()
    """

    return

def main(request):
    
    t = loader.get_template("main/index.html")
    return render_to_response('main/index.html', context_instance=RequestContext(request))



def upload(request):
    
    
    return render_to_response('upload/index.html', context_instance=RequestContext(request))


def results(request):

    if request.method == "POST":
        
        try:
            form = UploadFile(request.POST, request.FILES['img_file'])
            if form.is_valid():
                print "FUCK YEAH"
                #handle_img_search(request.FILES['img_file'])
                return render_to_response("results/index.html", context_instance=RequestContext(request))
            else:
                return HttpResponse("Invalid form input...")
        except:
            return HttpResponse("Error using image in search...")

    else:
        form = UploadFile()
                    

    return render_to_response("main/index.html", {'form':form})





def complete(request):
    
    return render_to_response('upload/complete.html', context_instance=RequestContext(request))


def upload_file(request):
    try:
    	if request.method == 'POST':
            
            form = UploadFile(request.POST, request.FILES['img'])
            
            if form.is_valid():
                
                handle_img_upload(request.FILES['img'])
              
                return HttpResponseRedirect('/upload/complete')
            else:
                return HttpResponse("Invalid form input...")
        else:
            
            form = UploadFile()
    except:
        return HttpResponse("Error During Upload")
        
    return render_to_response("upload/index.html", { 'form':form} )
    
