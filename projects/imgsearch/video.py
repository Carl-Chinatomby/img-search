from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response
from django import forms
from django.db import models

#import django.utils.datastructures.SortedDict

from imgsearch.models import Histograms, Images, Keywords

import StringIO
from PIL import Image, ImageDraw

from itertools import chain
from operator import itemgetter

from edit_dist import EditDistance

import json

import sys, os, zipfile


def calculate_hist(f):
    
    try:
        
        image = Image.open(StringIO.StringIO(f))
    except IOError:
        print "Error Opening Image file (PIL)"
        exit(0)
    try:
        hist = image.histogram()
    except:
        print "Unexpected error:", sys.exc_info()
        exit(0)
        
    hist16bin = []

    start = 0
    end = 16

    bin_count = 0
    hist16bin.append(0)

    for i in range(len(hist)):
        if i % 16 == 0:
            
            start = i
            end = start + 16
            if bin_count == 15:
                break
            bin_count += 1
            hist16bin.append(0)
            
        else:
            hist16bin[bin_count] += hist[i]
            
    """
    print "\n\n"
    print "16 Bin histogram: ", hist16bin
    print 
    print "Size: ", len(hist16bin)
    print "Original Size: ", len(hist)
    """

    return hist16bin

def get_consecutive_hist(f, IMAGE_DIR, VIDEO_DIR):
    """ 
    This function calculates the histograms inside
    the uploaded video, and returns a list of histograms
    (consecutively)
    """
    
    print "Image: ", IMAGE_DIR
    print "Video: ", VIDEO_DIR
    
    FILE_PATH = str(IMAGE_DIR) + '/' + str(f.name)

    print "FilePath: " + FILE_PATH 

    iz = zipfile.ZipFile(f, "r")         #Input Zip File
    #oz = zipfile.ZipFile(FILE_PATH) #Output of the Zip File
    print "\nIs it a zip file? ", iz.namelist(), "\n"

    # Here, I open the files inside the archive by name. 
    # It is important to note that these are not actual Python
    # file objects.  These are file-like objects, that only provide
    # read access (read(), readline(), readlines(), __iter__(), next()).
    """ Example iz archive list: 
             ['video/', 'video/clip1/', 
              'video/clip1/frame4.jpg', 
              'video/clip1/frame3.jpg', 
              'video/clip1/frame0.jpg',
              'video/clip1/frame2.jpg', 
              'video/clip1/frame1.jpg']
    """     

    basename = f.name[:-4] + '/clip1/'

    try:
        frame0 = iz.open(basename+'frame0.jpg')
        hist0 = calculate_hist(frame0.read())
        frame0.close()
        frame1 = iz.open(basename+'frame1.jpg')
        hist1 = calculate_hist(frame1.read())
        frame1.close()
        frame2 = iz.open(basename+'frame2.jpg')
        hist2 = calculate_hist(frame2.read())
        frame2.close()
        frame3 = iz.open(basename+'frame3.jpg')
        hist3 = calculate_hist(frame3.read())
        frame3.close()
        frame4 = iz.open(basename+'frame4.jpg')    
        hist4 = calculate_hist(frame4.read())
        frame4.close()
    except:
        print "Error Opening Files From Zip Archive!"

    
    
    
    
    

    print hist0
    print hist1
    print hist2
    print hist3
    print hist4

    
    
    
    
    

    iz.close()

    # First, we get the files from the archive, there is a specific format
    # which is root_folder/[clip#]/[frame#]

    # First, we change directory     

    return { 0:hist0, 1:hist1, 2:hist2, 3:hist3, 4:hist4 }
