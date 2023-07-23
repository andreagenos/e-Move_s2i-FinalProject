from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Auction_Item(models.Model):
    id = models.IntegerField(primary_key=True)
    product_title = models.CharField(max_length=20)
    description = models.TextField(max_length=500)
    startingbid = models.FloatField()
    price = models.FloatField(default= startingbid)
    image = models.ImageField(blank=True, null=True, upload_to= "images/")
    status = models.CharField(max_length=10, choices=(("active", "active"), ("closed", "closed")), default='active')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    winner = models.CharField(max_length=20, blank=True, null=True)
    txId = models.CharField(max_length=66, default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Auction_Item, self).save(*args, **kwargs)

class Bid(models.Model):
    auction = models.ForeignKey(Auction_Item, on_delete=models.CASCADE, default=1)
    bid_amount = models.FloatField()
    bidder_name = models.CharField(max_length=100, null=True)

    def save(self, *args, **kwargs):
        super(Bid, self).save(*args, **kwargs)

