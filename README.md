Project Specification
=====================

### Note: 
This is meant to be a group work. Each group may have up to three members.

# Deadline: the last lecture is the demo session for each group
 
> 1.a disk/cd containing your source code and executable file
> 2.you have to explain your implementation details during the demo
> session
> 3.a README file describing some technical details
> 4.GUI is REQUIRED.


 Missing any of the above items will cost you 10% of the score
allocated to this project.
 
  
# indexing phase: 
> three types of data need to be handled (only gray scale
> images/videos are considered):
> 1.text: words present in titles and descriptions for each image/video
> should be indexed by their frequencies.
> 2.image: Use the 16-bin histogram of the original and edge map of each
> image as the index for each image.
> 3.video: your system processes a sequence of input images simulating a
> raw video, e.g., 5 images from one clip and there are more than one
> clip in the input "raw video". Use difference of histogram to detect
> scene cuts for the input image sequence and three images for each
> sequence are indexed as the representation of each clip: the first,
> middle, and the last. Use the 16-bin histogram of the original and
> edge map of each image as the index for each representative frame.

# query phase:
> Find top matching images/videos for an image posed by users
> based on the similarities of the  
> given query image I and/or keyword(s). The distance is
> determined by the corresponding 
> 1.two 16-bin histograms: intensity and edge; and/or 
> 2.matching keywords based on edit distance and saved frequencies.
