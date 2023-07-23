from django import forms
from .models import Auction_Item, Bid

class Auction_Item_Form(forms.ModelForm):
    product_title = forms.CharField(required=True)
    description = forms.CharField(required=True)
    startingbid = forms.FloatField(required=True)
    image = forms.ImageField(required=True)

    class Meta:
        model = Auction_Item
        fields = ('product_title', 'description', 'startingbid', 'image')

class BidForm(forms.ModelForm):
    auction_id = forms.CharField()
    bidder_name = forms.CharField()
    bid_amount = forms.FloatField()
    

    class Meta:
        model = Bid
        fields = ('auction_id','bidder_name', 'bid_amount')
