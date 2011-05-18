from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.db import models
from imgsearch.models import Histograms, Images, Keywords
import StringIO
from PIL import Image, ImageDraw
from itertools import chain
from operator import itemgetter
from edit_dist import EditDistance
import json
import sys, os, zipfile, shutil
import logging as log

from imgsearch.models import *


# Here be dragons...

def calculate_hist(path, t, flag):

    try:
        image = Image.open(path)
    except IOError:
        print "Error Opening Image file (PIL)"

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
    
    # Now we put the histogram in the database
    if flag == True:
        normal = Histograms()
        normal.bin0 = hist16bin[0]
        normal.bin1 = hist16bin[1]
        normal.bin2 = hist16bin[2]
        normal.bin3 = hist16bin[3]
        normal.bin4 = hist16bin[4]
        normal.bin5 = hist16bin[5]
        normal.bin6 = hist16bin[6]
        normal.bin7 = hist16bin[7]
        normal.bin8 = hist16bin[8]
        normal.bin9 = hist16bin[9]
        normal.bin10 = hist16bin[10]
        normal.bin11 = hist16bin[11]
        normal.bin12 = hist16bin[12]
        normal.bin13 = hist16bin[13]
        normal.bin14 = hist16bin[14]
        normal.bin15 = hist16bin[15]
        normal.hist_type = t
        normal.save()

    return hist16bin

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
    the uploaded video, and returns a list of dictionaries
    mapping a frame number (0, 1, 2..) to a histogram for
    that frame.  Each list entry in the List represents
    an entire clip.
    """
    
    print "Image: ", IMAGE_DIR
    print "Video: ", VIDEO_DIR
    
    FILE_PATH = str(IMAGE_DIR) + '/' + str(f.name)
    
    print "FilePath: " + FILE_PATH 

    iz = zipfile.ZipFile(f, "r")         #Input Zip File
    
    OUT_PATH = str(IMAGE_DIR) + '/' + f.name[:-4]
    
    iz.extractall(IMAGE_DIR)

    # Save the actual zip file to the directory!
    destination = open(IMAGE_DIR + '/' + f.name, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


    destination.close()
    iz.close()

   

    # Added for loop to handle case where there is more than 
    # 1 clip.
    List = []
    for j in range(len(os.listdir(OUT_PATH))):
        hists = {}
        clip = '/clip' + str(j) + '/'
        for i in range(len(os.listdir(OUT_PATH + clip))):
            filen = OUT_PATH + clip + 'frame' + str(i) + '.jpg'
            hists[i] = calculate_hist(filen)
        
        List.append(hists)
        
    print List

    # First, we get the files from the archive, there is a specific format
    # which is root_folder/[clip#]/[frame#]

    # First, we change directory     

    return List



def get_sequence(hists):
    """
        This is the generalized sequence algorithm.
        It returns a mapping of clip numbers (dictionary)
        to clip sequences, which are of the form: [[seq1], [seq2], etc]
        so for clip 0, with 3 sequences, it would look like this:
        { 0: [[1, 2], [3], [4, 5]], ...}
    """
    threshold = 2.0

    # I'm normalizing (0 to 100) as well as calculating the difference below
    
    # Sequence Algorithm  
    clips_seqs = {}
    clip_count = 0  
    for histograms in hists:
        diffs = []
        seq = [[]]

        for i in range(len(histograms) - 1):
            flat0 = [histograms[i], histograms[i+1]]  
            flat0 = [item for sublist in flat0 for item in sublist] # This flattens the list of lists
            diffs.append((abs(sum(histograms[i], 0.0) / len(histograms[i]) - sum(histograms[i+1], 0.0) / len(histograms[i+1])) / max(flat0)) * 100.0)

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

        clips_seqs[clip_count] = seq
        clip_count += 1

    return clips_seqs


def seq_into_db(filename, seq, hist, title, desc):
    """
    seq: {0:[[1, 2],...]...}
    hist [{0:[122, 123, 2, 3, ...]}, { 1:[23,422,445]...} ... ]
    """

    video = Videos()
    
    video.filename = filename
    video.title = title
    video.description = desc
    
    clips = []
    
    """
    # Now, we get the list of clips
    for i in seq.iteritems():
        c = Clip()
        frames = find_frames(i)
        c.start_filename = 'frame' + frames[0]
        c.mid_filename = 'frame' + frames[1]
        c.end_filename = 'frame' + frames[2]

        
        c.orig_hist_clips = None
        c.orig_hist_clips = None


        # I need to get the last id, so I can add it to the
        # video tuple above...

    """
    
    return

    
def find_frames(seq):
    """
    takes a list of sequences and returns three frames.
    """
    count = 0
    f = []
    l = len(seq)
    for i in range(l):

        if count == 3:
            return f
        if l == 1:
            return [seq[i][0], seq[i][len(seq[i])/2], seq[i][len(seq[i])-1]]
        elif l == 2:
            if len(seq[i]) >= 3:
                f.append(seq[i][0])
                f.append(seq[i][len(seq[i])/2])
                count +=2
            else:
                f.append(seq[i][0])
        else:
            f.append(seq[i][len(seq[i])/2])
            count +=1
    return f
