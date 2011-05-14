# Create your views here.

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response
from django import forms
from django.db import models

from imgsearch.models import Histograms, Images, Keywords

import StringIO
from PIL import Image, ImageDraw

from itertools import chain

import json

import sys

#This needs to point to your repository static/image folder!
#IMAGE_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/images'
IMAGE_DIR = '/home/carl/git/img-search/projects/imgsearch/static/images'

#This needs to point to your repository static/videos folder!
#VIDEO_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/videos'
VIDEO_DIR = '/home/carl/git/img-search/projects/imgsearch/static/videos'



#class to hold the result to display

class QueryResult:
    def __init__(self):
        self.filename = ''
        self.percent = 0.0
        self.rank = 0.0


def img_rank(histograms):
    
    result = []
    result1 = []

    norm_diff = [0 for i in range(16)]
    edge_diff = [0 for i in range(16)]

    cur_norm = histograms[0]
    cur_edge = histograms[1]

    all_norms = Histograms.objects.filter(hist_type='n').all().values()
    all_edge  = Histograms.objects.filter(hist_type='e').all().values()


    """
    Each bin represents a different picture in the database.  What I'm doing
    here is simply comparing the current pictures histogram (bin by bin) with 
    all of the picutures histograms which are stored in the database.  This first
    case is only for the normal images.  The next case is for the edge map.
    """
    j = 0
    for norm in all_norms:
        i = 0

        res = QueryResult()
        for k, v in norm.iteritems():
            
            norm_diff[i] = abs(norm['bin' + str(i)] - cur_norm[i])
            m = max((norm['bin' + str(i)], cur_norm[i]))
            if m != 0:
                res.percent += abs( 100.0 * (norm_diff[i]/ float(m)) )
                print "Histogram #%d Bin %d Difference = %f" % (j, i, abs( 100.0 * (norm_diff[i]/ float(m)) ))
            else:
                print "Histogram #%d Bin %d Difference = %f" % (j, i, 0)

            i += 1
            if i >= 16:
                break
        res.percent = res.percent/16.0
        result.append(res)
        print "Cummulative difference for Histogram #%d = %f" % (j, result[j].percent)
        j += 1

    print "\n Edge Map: "
    j = 0
    for edge in all_edge:
        i = 0

        res = QueryResult()
        for k, v in edge.iteritems():
            
            edge_diff[i] = abs(edge['bin' + str(i)] - cur_edge[i])
            m = max((edge['bin' + str(i)], cur_edge[i]))
            if m != 0:
                res.percent += abs( 100.0 * (edge_diff[i]/ float(m)) )
                print "Histogram #%d Bin %d Difference = %f" % (j, i, abs( 100.0 * (edge_diff[i]/ float(m)) ))
            else:
                print "Histogram #%d Bin %d Difference = %f" % (j, i, 0)

            i += 1
            if i >= 16:
                break
        res.percent = res.percent/16.0
        result1.append(res)
        print "Cummulative difference for Histogram #%d = %f" % (j, result1[j].percent)
        j += 1
            
    
    return 


class UploadFile(forms.Form):
    name = models.ImageField()
    

def handle_img_upload(f):
    """ 
    This function uploads images, saves them in a directory.
    The, it goes and calculates the normal and edge histograms
    and puts that information in the database.
    """
    
    path = IMAGE_DIR + '/' + f.name
    tmp_file = IMAGE_DIR + '/tmp.jpg'

    print path
    
    try:    
        o = open(path, "wb")
        
        
    except IOError:
        print "Error opening file for writing!"
        exit(-1)

    f.open()
    for chunk in f.chunks():
        o.write(chunk)
    
    f.close()
    o.close()

    # At this point, the file is in the images folder, and we can
    # do processing on it.
    calculate_hist(path, 'n')

    # Next, we generate a edge map.  We can use various 
    # methods, but I went with the easiest for this, which is a basic gradient edge detection

    gradient(path, tmp_file)

    
    #Finally, we calculate the edge map histogram
    calculate_hist(tmp_file, 'e')
    

    return

def calculate_hist(path, t):
    """ Returns a length 16 list """
    try:
        image = Image.open(path)
    except IOError:
        print "Error Opening Image file (PIL)"

    #print "Format: ", image.format, " Size: ", image.size, " Mode: ", image.mode

    # This is so neat!  A histogram method!  Hopefully the professor doesn't disapprove.
    
    #print "Histogram: ", image.histogram()

    # However, we must make it a 16 bin historgram.
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
            
    print "\n\n"
    print "16 Bin histogram: ", hist16bin
    print 
    print "Size: ", len(hist16bin)
    print "Original Size: ", len(hist)
    
    # Now we put the normal histogram in the database

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

def gradient(filename, new_filename):
    """ This function generates a edge map on the given
        filename image.  It outputs a grayscale image 
        map."""

    threshold = 255

    Ix = ((-1, 0, -1),
          (-1, 0, -1),
          (-1, 0, -1)
         )
    Iy = ((-1, -1, -1),
          (0 , 0 ,  0),
          (-1, -1, -1)
         )

    try:
        image = Image.open(filename)
    except IOError:
        print "Error opening image file!"
        exit(-1)


    # Generate a luminecanse image (Grayscale) of the same size and mode (L)
    edge_map = Image.new(image.mode, image.size)
    #image.show()


    # Create a drawable object
    draw = ImageDraw.Draw(edge_map)


    for x in range(1, image.size[0] - 1):
        for y in range(1, image.size[1] - 1):
            IxVal = 0
            IyVal = 0
            for i in range(3):
                for j in range(3):
                    IxVal += Ix[i][j]*image.getpixel((x + i - 1, y + j - 1))
                    IyVal += Iy[i][j]*image.getpixel((x + i - 1, y + j - 1))
                    
                        
            #res = math.sqrt((IxVal**2) + (IyVal**2))        
            res = abs(IxVal) + abs(IyVal)

            if res > threshold:
                draw.point((x, y), fill=255)
            else:
                draw.point((x, y), fill=0)

    # Finished drawing
    del draw

    data = StringIO.StringIO()
    edge_map.save(data, "JPEG")

    #edge_map.show()

    out = open(new_filename, "wb")

    out.write(data.getvalue())
    out.close()
    

    return



def img_only_search(f):
   
    
    tmp_img = IMAGE_DIR + '/cur_pic.jpg'
    tmp_img_edge = IMAGE_DIR + '/cur_pic_edge.jpg'

    try:    
        o = open(tmp_img, "wb")
        
    except IOError:
        print "Error opening file for writing!"
        exit(-1)

    f.open()
    for chunk in f.chunks():
        o.write(chunk)
    
    f.close()
    o.close()
    

    ## Now, we calculate the edge and intensity histograms of this image...

    norm_hist = calculate_hist(tmp_img, 'n')
    gradient(tmp_img, tmp_img_edge)
    edge_hist = calculate_hist(tmp_img_edge, 'e')

    #Now, we pass the information to the calling method so we can pass it 
    #to the template for display

   

    return [norm_hist, edge_hist]

def main(request):
    
    t = loader.get_template("main/index.html")
    return render_to_response('main/index.html', context_instance=RequestContext(request))



def upload(request):
    
    
    return render_to_response('upload/index.html', context_instance=RequestContext(request))


def results(request):

    
    if request.method == "POST":
        # First determine whats being included in the search
        try: 
            img = request.FILES['img_file']
        except:
            img = None

        try:
            text = request.POST['search_box']
            if text == '':
                text = None
        except: 
            text = None
        print "text ", text, " img: ", img
        
        if img == None and text != None:
            # text only search
            text_only_search(text)

        elif img != None and text == None:
            # img only search   
           
            print  " img: ", request.FILES['img_file'].content_type

            if request.FILES['img_file'].content_type != "image/jpeg":
                return HttpResponse("Must be JPEG!")

            form = UploadFile(request.POST, request.FILES['img_file'])

            histograms = img_only_search(request.FILES['img_file'])

            results = img_rank(histograms)
            

            return render_to_response("results/index.html", {'histograms': json.dumps(histograms), 'img_path' : request.FILES['img_file'].name, 'query': '', 'results':results})
            
            #return render_to_response("results/index.html", context_instance=RequestContext(request))
            pass

        elif img != None and text != None:
            # text AND img search        
            pass



            

        """
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
        """
    
                    

    return HttpResponseRedirect("/")





def complete(request):
    
    return render_to_response('upload/complete.html', context_instance=RequestContext(request))


def upload_file(request):
    print request.POST['textarea']
    print 
    print request.POST['title']

    try:
    	if request.method == 'POST':
            
            form = UploadFile(request.POST, request.FILES['img'])
            
            if form.is_valid():
                
                #We test to see if the given image is of L band (true Grayscale)
                test_grayscale = Image.open(StringIO.StringIO(request.FILES['img'].read()))
                if test_grayscale.mode != 'L':
                    return HttpResponse("Image is not grayscale!  Has " + test_grayscale.mode + " band.  Needs 'L' for true Grayscale!")
                handle_img_upload(request.FILES['img'])

                # We know that the normal histogram is inserted into the database
                # first, and the edge second, so we can do this hack:
                edge_id = Histograms.objects.order_by('id').values('id')[len(Histograms.objects.all()) - 1]['id']
                norm_id = Histograms.objects.order_by('id').values('id')[len(Histograms.objects.all()) - 2:len(Histograms.objects.all()) - 1].get()['id']
                
                # Here, we insert the Images information, now that we have the two IDs above.

                img = Images()
               
                print str(request.FILES['img'].name)
                print int(norm_id)
                print int(edge_id)
                print str(request.POST['title'])
                print str(request.POST['textarea'])
                
                img.filename = str(request.FILES['img'].name)
                img.orig_hist = int(norm_id)
                img.edge_hist = int(edge_id)
                img.title = str(request.POST['title'])
                img.description = str(request.POST['textarea'])
                img.save()
                index_img_kw(img, img.title, img.description)

                return HttpResponseRedirect('/upload/complete')
            else:
                return HttpResponse("Invalid form input...")
        else:
            
            form = UploadFile()
    except:
        return HttpResponse("Error During Upload")
        
    return render_to_response("upload/index.html", { 'form':form} )
   

STOP_WORDS = ['I', 'a', 'about', 'an', 'are', 'as', 'at', 'be', 'by', 'com', 
'for', 'from', 'how', 'in', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 
'this', 'to', 'was', 'what', 'when', 'where', 'who', 'will', 'with', 'the',
'www',
]

def index_img_kw(img, title, description):
    """
    Parses the the title and description and creates a frequency table,
    then stores the frequencies into the Keywords table for the given
    image_id
    """
    print "in this function"
    #build frequency table for the keywords
    frequencies = {}
    title_kws = title.split()
    des_kws = description.split()
    #titles count as double weight
    for word in title_kws:
        if word not in STOP_WORDS:
            word = word.lower()
            frequencies[word] = frequencies[word] + 2 if word in frequencies else 2
    print "title frequencies are"
    print frequencies
    
    for word in des_kws:
        if word not in STOP_WORDS:
            word = word.lower()
            frequencies[word] = frequencies[word] + 1 if word in frequencies else 1
    
    print "frequencies after the descriptions are"
    print frequencies
    
    #Save in database now for this image
    try:
        for entry, val in frequencies.items():
        
            kw = Keywords()
            kw.keyword = entry.lower()
            kw.frequency = val
            kw.image = img
            kw.save()
    except:
        print sys.exc_info()
       
        
def text_only_search(text):
    search_words = text.split()
    
    #remove duplicates
    search_words = list(set(search_words))
    
    results = []
    #exact keyword matches
    for word in search_words:
        if word not in STOP_WORDS:
           cur_res = Keywords.objects.filter(keyword__iexact=word).order_by('-frequency')  
           results = list(chain(results, cur_res))

    print results
           #now we need to rank the results for images based on most exact matches
    rankedres = rank_results(results)
    
    #substring matches
    
    #edit distance matches
    
    return results
    
def rank_results(results):
    """
    retuns results ranked by the highest points. The formula used
    to calculate points is: points = #keywords_matched * cumfreq
    """
    #we're going to create a table based on image, number of keywords matched 
    #and use frequency to break the ties
    
    #image, frequency, keywords, points (points = #of keywords * cumfreq)
    ranked_res = []
    frequency = {}
    kwnum = {}
    points = {}
    
    print "in ranking"
    for result in results:
        imgid = result.image.id
        if imgid in frequency:
            frequency[imgid] += result.frequency
            kwnum[imgid] += 1
        else:
            frequency[result.image.id] = result.frequency
            kwnum[imgid] = 1
        
        points[imgid] = frequency[imgid] * kwnum[imgid]
    
    
    print "the frequency are: "    
    print frequency
    print "the kwnum are: "    
    print kwnum
    print "the points are: "    
    print points     
   