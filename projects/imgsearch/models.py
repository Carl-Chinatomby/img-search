from django.db import models

# Create your models here.

class Histograms(models.Model):
    id = models.AutoField(primary_key=True)
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

    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=255)
    orig_hist = models.IntegerField()
    edge_hist = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()

