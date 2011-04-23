# Create your views here.

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response
from django import forms
from django.db import models

from imgsearch.models import Histograms, Images

import StringIO
from PIL import Image, ImageDraw


import json


#This needs to point to your repository static/image folder!
IMAGE_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/images'

#This needs to point to your repository static/videos folder!
VIDEO_DIR = '/home/prototype/repos/git/img-search/projects/imgsearch/static/videos'




#class to hold the result to display

class QueryResult:
    def __init__(self):
        self.filename = ''
        self.percent = 0
        self.rank = 0


def img_rank(histograms):
    
    result = []

    norm_diff = [0 for i in range(16)]
    edge_diff = [0 for i in range(16)]

    cur_norm = histograms[0]
    cur_edge = histograms[1]

    all_norms = Histograms.objects.filter(hist_type='n').all()
    all_edge  = Histograms.objects.filter(hist_type='e').all()

    for bin in all_norms:
        res = QueryResult()
        
        norm_diff[0] = bin.bin0 - cur_norm[0]
        m = max((bin.bin0, cur_norm[0]))
         
        if m != 0:
            res.percent += abs( norm_diff[0]/m )
        
        norm_diff[1] = abs(bin.bin1 - cur_norm[1]) 
        m = max((bin.bin1, cur_norm[1]))
         
        if m != 0:
            res.percent += abs( norm_diff[1]/m )
         
        norm_diff[2] = abs(bin.bin2 - cur_norm[2])

        m = max((bin.bin2, cur_norm[2]))
         
        if m != 0:
            res.percent += abs( norm_diff[2]/m )
    
        norm_diff[3] = abs(bin.bin3 - cur_norm[3])

        m = max((bin.bin3, cur_norm[3]))
         
        if m != 0:
            res.percent += abs( norm_diff[3]/m )

        norm_diff[4] = abs(bin.bin4 - cur_norm[4])
        m = max((bin.bin4, cur_norm[4]))
         
        if m != 0:
            res.percent += abs( norm_diff[4]/m )

        norm_diff[5] = abs(bin.bin5 - cur_norm[5])

        m = max((bin.bin5, cur_norm[5]))
         
        if m != 0:
            res.percent += abs( norm_diff[5]/m )
        norm_diff[6] = abs(bin.bin6 - cur_norm[6])

        m = max((bin.bin6, cur_norm[6]))
         
        if m != 0:
            res.percent += abs( norm_diff[6]/m )

        norm_diff[7] = abs(bin.bin7 - cur_norm[7])
        
        m = max((bin.bin7, cur_norm[7]))
         
        if m != 0:
            res.percent += abs( norm_diff[7]/m )

        norm_diff[8] = abs(bin.bin8 - cur_norm[8])
        m = max((bin.bin8, cur_norm[8]))
         
        if m != 0:
            res.percent += abs( norm_diff[8]/m )
        norm_diff[9] = abs(bin.bin9 - cur_norm[9])
        m = max((bin.bin9, cur_norm[9]))
         
        if m != 0:
            res.percent += abs( norm_diff[9]/m )

        norm_diff[10] = abs(bin.bin10 - cur_norm[10])
        m = max((bin.bin10, cur_norm[10]))
         
        if m != 0:
            res.percent += abs( norm_diff[10]/m )
        norm_diff[11] = abs(bin.bin11 - cur_norm[11])
        m = max((bin.bin11, cur_norm[11]))
         
        if m != 0:
            res.percent += abs( norm_diff[11]/m )
        norm_diff[12] = abs(bin.bin12 - cur_norm[12])

        m = max((bin.bin12, cur_norm[12]))
         
        if m != 0:
            res.percent += abs( norm_diff[12]/m )

        norm_diff[13] = abs(bin.bin13 - cur_norm[13])

        m = max((bin.bin13, cur_norm[13]))
         
        if m != 0:
            res.percent += abs( norm_diff[13]/m )

        norm_diff[14] = abs(bin.bin14 - cur_norm[14])

        m = max((bin.bin14, cur_norm[14]))
         
        if m != 0:
            res.percent += abs( norm_diff[14]/m )
        norm_diff[15] = abs(bin.bin15 - cur_norm[15])
        m = max((bin.bin15, cur_norm[15]))
         
        if m != 0:
            res.percent += abs( norm_diff[15]/m )
        
            
        print "Total Percent Difference: ", res.percent,"%"


    #for a_hist in all_edge:
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

    hist = image.histogram()
    
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
            pass

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
                

                return HttpResponseRedirect('/upload/complete')
            else:
                return HttpResponse("Invalid form input...")
        else:
            
            form = UploadFile()
    except:
        return HttpResponse("Error During Upload")
        
    return render_to_response("upload/index.html", { 'form':form} )
    
