# Create your views here.

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

import sys
import string

from imgsearch.video import *


#This needs to point to your repository static/image folder!
#IMAGE_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/images'
IMAGE_DIR = '/home/carl/git/img-search/projects/imgsearch/static/images'
#IMAGE_DIR = '/home5/bluemedi/.local/lib/python2.7/site-packages/projects/imgsearch/static/images'

#This needs to point to your repository static/videos folder!
#VIDEO_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/videos'
VIDEO_DIR = '/home/carl/git/img-search/projects/imgsearch/static/videos'
#VIDEO_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/videos'


#class to hold the result to display
class QueryResult:
    """
    A Result class that represents an object to be passed to the templates on the results page
    """
    def __init__(self):
        self.id = 0
        self.filename = ''
        self.histogram = None
        self.percent = 0.0
        self.rank = 0.0
        self.title = ''
        self.description = ''
        #Video Fields
        self.video = False
        self.framename = None
    
    def __cmp__(self, other):
        if self.precent < other.percent:
            return -1
        elif self.precent == other.percent:
            return 0
        else:
            return 1
        
def sort_query_results(qrlst, attr=id):
    """
    Query Result Toolkit Function
    Sorts a list of Query Result Objects by the attribute given
    """
    
    
    print "origoinal list is"
    print qrlst
    ranked = [(getattr(qr, attr), qr) for qr in qrlst].sort() #returns a list of tuples sorted by id
    print ranked
    return [ entry[1] for entry in ranked ] if ranked else ranked
#------
        

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
    Each histogram represents a different picture in the database.  What I'm doing
    here is simply comparing the current pictures histogram (bin by bin) with 
    all of the pictures histograms which are stored in the database.  This first
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
                #print "Histogram #%d Bin %d Difference = %f" % (j, i, abs( 100.0 * (norm_diff[i]/ float(m)) ))
            else:
                #print "Histogram #%d Bin %d Difference = %f" % (j, i, 0)
                pass

            i += 1
            if i >= 16:
                break
        res.id = int(norm['id'])
        print 
        print "ID: ",
        print res.id
        res.filename = Images.objects.all().values().get(orig_hist=res.id)['filename']
        res.percent = res.percent/16.0
        res.title = Images.objects.all().values().get(orig_hist=res.id)['title']
        res.description = Images.objects.all().values().get(orig_hist=res.id)['description']
        if res.percent != 100.0:
            result.append(res)
        #print "Cummulative difference for Histogram #%d = %f" % (j, result[j].percent)
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
                #print "Histogram #%d Bin %d Difference = %f" % (j, i, abs( 100.0 * (edge_diff[i]/ float(m)) ))
            else:
                #print "Histogram #%d Bin %d Difference = %f" % (j, i, 0)      
                pass

            i += 1
            if i >= 16:
                break
        
        res.id = int(edge['id'])
        print 
        print "ID: ",
        print res.id
        res.filename = Images.objects.all().values().get(edge_hist=res.id)['filename']
        res.title = Images.objects.all().values().get(edge_hist=res.id)['title']
        res.description = Images.objects.all().values().get(edge_hist=res.id)['description']
        res.percent = res.percent/16.0
        if res.percent != 100.0:
            result1.append(res)
        #print "Cummulative difference for Histogram #%d = %f" % (j, result1[j].percent)
        j += 1
            
    
    # return both results
    #print sorted(result)
    return [result, result1]


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
    calculate_hist(path, 'n', True)

    # Next, we generate a edge map.  We can use various 
    # methods, but I went with the easiest for this, which is a basic gradient edge detection

    gradient(path, tmp_file)

    
    #Finally, we calculate the edge map histogram
    calculate_hist(tmp_file, 'e', True)
    

    return

def calculate_hist(path, t, flag):
    """ Returns a length 16 list
        The third parameter is a flag.  It says that if it's set
        to false, we should not put the calcuated histograms in the
        database.  And we should if it's true.  This came about because
        of the fact that search image histograms do not need to be put in the database
        while uploaded images do.  And since I use the same function to calculate the
        histograms there is no need to rewrite code, just set a flag."""
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

    pix = image.load()
    for x in range(1, image.size[0] - 1):
        for y in range(1, image.size[1] - 1):
            IxVal = 0
            IyVal = 0
            for i in range(3):
                for j in range(3):
                    #IxVal += Ix[i][j]*image.getpixel((x + i - 1, y + j - 1))
                    #IyVal += Iy[i][j]*image.getpixel((x + i - 1, y + j - 1))

                    # This modification should prove to be very fast compared to the above
                    
                    IxVal += Ix[i][j]*pix[x + i - 1, y + j - 1]
                    IyVal += Iy[i][j]*pix[x + i - 1, y + j - 1]

  
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
    norm_hist = calculate_hist(tmp_img, 'n', False)
    gradient(tmp_img, tmp_img_edge)
    edge_hist = calculate_hist(tmp_img_edge, 'e', False)

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
            res = text_only_search(text)
            
            return render_to_response("results/index.html", {'query': text, 'results':res})
            

        elif img != None:
            # img only search   
           
            print  " img: ", request.FILES['img_file'].content_type

            if request.FILES['img_file'].content_type != "image/jpeg":
                return HttpResponse("Must be JPEG!")

            form = UploadFile(request.POST, request.FILES['img_file'])

            histograms = img_only_search(request.FILES['img_file'])


            """ At this point, the two elements in the results list 
                correspond to the same image information, but for two
                histograms, namely normal and edge map histograms.  I
                interleave the results.
            """         
            results = img_rank(histograms)
            res = []
            for i in range(len(results[0])):
            
                results[0][i].percent = 100.0 - results[0][i].percent;
                res.append(results[0][i])
                    
                """
                if i & 1 == 0:
                    results[0][i].percent = 100.0 - results[0][i].percent;
                    res.append(results[0][i])
                    
                else:
                    results[1][i].percent = 100.0 - results[1][i].percent;
                    res.append(results[1][i])
                """
            print results
            if text == None:
                return render_to_response("results/index.html", {'histograms': json.dumps(histograms), 'img_path' : request.FILES['img_file'].name, 'query': '', 'results':res})
                #return render_to_response("results/index.html", context_instance=RequestContext(request))
            else:
                # text AND img search        
                print "testing txt and img search"
                
                txt_res = text_only_search(text)
                print "the text results were"
                print txt_res
                print "the img results were"
                print res
                res = txt_hist_res_merge(txt_res, res)
                print "the merged results are"
                print res
                return render_to_response("results/index.html", {'histograms': json.dumps(histograms), 'img_path' : request.FILES['img_file'].name, 'query': '', 'results':res})


            

        """
        try:
            form = UploadFile(request.POST, request.FILES['img_file'])
            if form.is_valid():
                
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
            form = None
            
            try:
                res = request.FILES['img']
                
                """
                This part handles the image upload
                """
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
            except:
               
                try:
                    """
                    Here we upload the zipped file, and process 3 frames from 5
                    """
                    res = request.FILES['vid']

                    histograms = get_consecutive_hist(res, IMAGE_DIR, VIDEO_DIR)
                    print "\nNumber of histograms: ", len(histograms)
                    sequence = get_sequence(histograms)

                    return HttpResponseRedirect('/upload/complete')
                    
                except:
                    HttpResponse("Error uploading Video!")
            
        else:
            
            form = UploadFile()
    except:
        return HttpResponse("Error During Upload")
        
    return render_to_response("upload/index.html", { 'form':form}, context_instance=RequestContext(request) )
   

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
        word = word.lower()
        word = string.translate(word, None, string.punctuation)
        if word not in STOP_WORDS:
            frequencies[word] = frequencies[word] + 2 if word in frequencies else 2
    print "title frequencies are"
    print frequencies
    
    for word in des_kws:
        if word not in STOP_WORDS:
            word = word.lower()
            word = string.translate(word, None, string.punctuation)
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
    """
    performs a search and ranks results based on the text given (splits into individual words)
    """
    search_words = text.split()
    
    #remove duplicates
    search_words = list(set(search_words))
    
    results = []
    ed = EditDistance(Keywords, 'keyword')

    for word in search_words:
        if word not in STOP_WORDS:
            #exact and substring keyword matches incase-sensitive
            #####
            #cur_res = Keywords.objects.extra(select={'diff':"length(keyword)-length(%s)"}, select_params=[word]).filter(keyword__contains=word).order_by('diff','-frequency')
            #results = list(chain(results, cur_res))
            #print cur_res
            ####
            ed_list, ed_diff = ed.correct(word)
            for res in ed_list:
                #### Advanced search features for later
                #cur_res = Keywords.objects.extra(select={'diff':"length(keyword)-length(%s)+%d"}, select_params=[res, diff]).filter(keyword__contains=word)order_by('diff','-frequency')
                ####
                cur_res = Keywords.objects.extra(select={'diff':"%s"}, select_params=[ed_diff]).filter(keyword__exact=res).order_by('diff','-frequency')
                results = list(chain(results, cur_res))
                print cur_res
            #for res in cur_res:
            #   for kw in res:
            #       print "Keyword %s has frequency %d and diff %d" % (res.keyword, res.frequency, res.diff)

    print results
    #now we need to rank the results for images based on most exact matches
    ranked_res = rank_results(results)

    return ranked_res
    
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
    diff = {}
    ranker = {}
    print "in ranking"
    for result in results:
        imgid = result.image.id
        if imgid in frequency:
            ranker[imgid] = (ranker[imgid][0] + result.frequency, ranker[imgid][1]+result.diff)
            frequency[imgid] += result.frequency
            kwnum[imgid] += 1
            diff[imgid] += result.diff
        else:
            ranker[imgid] = (result.frequency, result.diff)
            frequency[result.image.id] = result.frequency
            kwnum[imgid] = 1
            diff[imgid] = result.diff
        
        points[imgid] = frequency[imgid] * kwnum[imgid]

    #ranked_diff = sorted(diff.iteritems(), key=itemgetter(1), reverse=True)
    #ranked_diff.reverse()
    #print ranked_diff
    #ranked_res = sorted(points, key=points.__getitem__, reverse=True)
    ranked_freq = sorted(ranker.iteritems(), key=itemgetter(1), reverse=True)
    #another.reverse()
    print ranked_freq
    ranked_diff = sorted(ranked_freq, key=lambda a: -a[1][1], reverse=True)
    print ranked_diff
    ranked_res = [ x[0] for x in ranked_diff ] 
    print ranked_res
    final_res = txt_queryres_from_imgid(ranked_res, points)
    print final_res
    return final_res

def txt_queryres_from_imgid(idlst, points):
    """
    idlst is a list of image id's ranked in descendingorder (the first element has the highest rank)
    the Points dictionary is passed in to set the percentages
    Returns a list of QueryResult objects 
    """
    cnt = 0
    results = []
    total_pts = sum([i for i in points.values()])
    for imgid in idlst:
        cnt += 1
        cur_res = QueryResult()
        cur_res.rank = cnt
        cur_image = Images.objects.get(id=imgid)
        cur_res.id = cur_image.id
        cur_res.filename = cur_image.filename
        cur_res.title = cur_image.title
        cur_res.description = cur_image.description
        cur_res.percent = points[cur_image.id] / float(total_pts) * 100
        results.append(cur_res)
    return results

def txt_hist_res_merge(txt_results, hist_results):
    """
    Assumes both txt_results and hist_results is not empty
    Finds the Intersection of results in both queries and recalculates the percentage where the
    new percentage is 50% textres percent + 50% histres percent and reranked accordingly
    """
    #the weight should add up to 1
    hres_weight = .50
    tres_weight = .50
    
    #Intersection Phase
    merged_results = []
    print "about to do the intersction"
    print "the txt_results before intesection is"
    print txt_results
    print "the hist res before intection is"
    print hist_results
    for tres in txt_results:
        for hres in hist_results:
            cur_res = QueryResult()
            print "the text id is" 
            print tres.id
            print "the hres id is"
            print hres.id
            if tres.id == hres.id: #intersection in both sets
                cur_res.id = tres.id
                cur_res.filename = tres.id
                cur_res.histogram = hres.histogram
                cur_res.rank = 0
                cur_res.percent = hres_weight * hres.percent + tres_weight * tres.percent
                cur_res.title = tres.title
                cur_res.description = tres.description
                merged_results.append(cur_res)
                break
    print "the merged results are: "
    print merged_results
    #Reranking Phase
    merged_results = sort_query_results(merged_results, 'percent') if merged_results else []
    
    return merged_results

def vid_img_merg(vid_results, img_results):
    """
    merged the ranked video and img results based on histogram means and standard deviations
    and reranks them accordingly
    """
    pass