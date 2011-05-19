from django.db import models

# Create your models here.

class Histograms(models.Model):
    id = models.AutoField(primary_key=True)
    hist_type = models.CharField(max_length=1)
    is_video = models.CharField(max_length=1, default='x')
    bin0 = models.IntegerField()
    bin1 = models.IntegerField()
    bin2 = models.IntegerField()
    bin3 = models.IntegerField()
    bin4 = models.IntegerField()
    bin5 = models.IntegerField()
    bin6 = models.IntegerField()
    bin7 = models.IntegerField()
    bin8 = models.IntegerField()
    bin9 = models.IntegerField()
    bin10 = models.IntegerField()
    bin11 = models.IntegerField()
    bin12 = models.IntegerField()
    bin13 = models.IntegerField()
    bin14 = models.IntegerField()
    bin15 = models.IntegerField()
    

class Images(models.Model):
    """
    This model stores the image information
    """
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=255)
    orig_hist = models.IntegerField()
    edge_hist = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()

class Clips(models.Model):
    """
    This model stores the clip histogram information.
    """
    id = models.AutoField(primary_key=True)
    orig_hist_clips = models.CommaSeparatedIntegerField(max_length=3)
    edge_hist_clips = models.CommaSeparatedIntegerField(max_length=3)
    start_filename = models.CharField(max_length=255)
    mid_filename = models.CharField(max_length=255)
    end_filename = models.CharField(max_length=255)

class Videos(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=255)
    clips = models.CommaSeparatedIntegerField(max_length=10)
    title = models.CharField(max_length=255)
    description = models.TextField()

class Keywords(models.Model):
    """
    This model stores the keyword and frequency
    for each image
    """
    keyword = models.TextField()
    image = models.ForeignKey(Images)
    frequency = models.IntegerField()
