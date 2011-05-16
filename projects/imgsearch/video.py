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

import logging as log

def calculate_hist(f):
   
    try:
        
        image = Image.open(StringIO.StringIO(f))
    except IOError:
        log.debug("IO Error in calculate_hist!")
        exit(0)
    try:
        hist = image.histogram()
    except:
        log.debug("Unexpected error:" + sys.exc_info())
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

    return hist16bin
    
    return None

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
    
    OUT_PATH = str(IMAGE_DIR) + '/' + f.name[:-4]
    
    iz.extractall(IMAGE_DIR)
    iz.close()

    hists = {}
    
    for i in range(len(os.listdir(OUT_PATH + '/clip1'))):
        print OUT_PATH + '/clip1/frame' + str(i) + '.jpg'
        fi = open(OUT_PATH + '/clip1/frame' + str(i) + '.jpg')
        hists[i] = calculate_hists(fi.read())
        fi.close()
        break
   

    print hists

    # First, we get the files from the archive, there is a specific format
    # which is root_folder/[clip#]/[frame#]

    # First, we change directory     

    return hists



def get_sequence(histograms):
    """
        returns three histograms
    """
    threshold = 10.0

    # I'm normalizing (0 to 100) as well as calculating the difference below
    
    flat0 = [histograms[0], histograms[1]]  
    flat0 = [item for sublist in flat0 for item in sublist] # This flattens the list of lists
    diff0 = (abs(sum(histograms[0], 0.0) / len(histograms[0]) - sum(histograms[1], 0.0) / len(histograms[1])) / max(flat0)) * 100.0
    flat0 = [histograms[1], histograms[2]]  
    flat0 = [item for sublist in flat0 for item in sublist] 
    diff1 = (abs(sum(histograms[1], 0.0) / len(histograms[1]) - sum(histograms[2], 0.0) / len(histograms[2])) / max(flat0)) * 100.0
    flat0 = [histograms[2], histograms[3]]  
    flat0 = [item for sublist in flat0 for item in sublist]
    diff2 = (abs(sum(histograms[2], 0.0) / len(histograms[2]) - sum(histograms[3], 0.0) / len(histograms[3])) / max(flat0)) * 100.0
    flat0 = [histograms[3], histograms[4]]  
    flat0 = [item for sublist in flat0 for item in sublist] 
    diff3 = (abs(sum(histograms[3], 0.0) / len(histograms[3]) - sum(histograms[4], 0.0) / len(histograms[4])) / max(flat0)) * 100.0
    
    sequence = [[]]
    diffs =  [diff0, diff1, diff2, diff3, diff4]
    for i in range(len(diffs)):
        
        
        pass

    print diff1
    print diff2
    print diff3
    print

    
    

    return 
