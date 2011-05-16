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
        
        image = Image.open(f)
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
    
    return ''

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
        filen = OUT_PATH + '/clip1/frame' + str(i) + '.jpg'
        hists[i] = calculate_hist(filen)
        
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
    
    diffs = []
    for i in range(len(histograms) - 1):
        flat0 = [histograms[i], histograms[i+1]]  
        flat0 = [item for sublist in flat0 for item in sublist] # This flattens the list of lists
        diffs.append((abs(sum(histograms[i], 0.0) / len(histograms[i]) - sum(histograms[i+1], 0.0) / len(histograms[i+1])) / max(flat0)) * 100.0)
    

    # Sequence Algorithm    
    seq = [[]]
    for i in range(len(diffs)):
        if diffs[i] < threshold:
            # This is a sequence        
            l = len(seq) - 1
            seq[l].append(i)
            if i + 1 == len(diffs):
                seq[l].append(i + 1)
            elif diffs[i + 1] > threshold:
                seq[l].append(i + 1)
                
        else:
            seq.append([])
            if i + 1 == len(diffs):
                seq[len(seq) - 1].append(i + 1)
            elif diffs[i + 1] > threshold:
                seq[len(seq) - 1].append(i + 1)
        
        pass

    print seq

    
    

    return 
