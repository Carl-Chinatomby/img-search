img-search
==========

By Carl Chinatomby, Eudis Duran, Reddy Chukkalore
-------------------------------------------------

##Indexing Phase:

###Text:
WHen an Image is uploaded, the title and the description is inputted.
We use a hashmap to build a frequency table for all the words (except
STOP words). We count title frequencies as double (Since a title match
is more relevant that a content match of the description). This
Resultant Frequency Table is then inserted into our database for the
word, imagename, and frequency count. 

###Images:
When an image is uploaded we create edge map and store histograms of
both the edge map and the original into our histograms database and
use the images database to relate to it.

###Video:
Video's are uploaded as a zip file. The zip file conists of several
clips which may have several sequences. This is extracted into a folder.
Histograms are created for each frame of the clip. We calculate the
differences between the histograms. If there difference is
higher then a thresholdvalue (constant set in program) then we determine
determine that a scene change has been made and create a list of lists
of frame numbers for that scene. We then have everything broken into
scenes. We take a frame from the first scene, middle scene, and last
scene and create edge maps and store the histograms in the database.
We do this for all the clips. We have A video Tables that has a
relation of several Clips that has 3 histograms each for the origional
image and the edge mapped image.

###Histograms:
For Histograms, we scan each pixel in the image and see if it what
range it falls into for [0-255]/16 and insert it into that bin
(increment it).

##Querying:

###Text:
For the text search we do edit distance on the image for 1 character.
If an exact result is met we stop. Otherwise we keep doing edit
distance for 2 characters, and so on until the count reaches the
length of the inputted string or we finally find a result. Those
results are then matched according to frequency.

###Images:
For images, we scan all histograms and compare the means and standard
devations and rank them by the difference of the inputted image. 

###Text and Images:
For text and images we find the intersection of text and image results
that match and then we rank them by 50% txtpercentage + 50%
imgpercentage. 

###Video:
Video Results are ranked the same as images. However the procedure to
search a video is different. We do an image search of the all the
histograms for video's and then we find the corresponding clip. We
then see what scene it matched and set the filename for that. Then we
Display the video in our result but indexed by the scene that matched.

###Edit Distance: Python Lists are created for the subsets of splits,
deletes, transposts, replaces, inserts, then a set is created for all
the ones that match by the 1 character change. 
