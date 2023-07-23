from django.shortcuts import render, redirect
from .forms import Auction_Item_Form
from django.http import HttpResponse, HttpResponseBadRequest
from .models import Auction_Item
from django.utils import timezone
from .forms import BidForm
import redis
from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from .models import Auction_Item
from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.models import User
import json
from .utils import sendTransaction
import hashlib
from django.core.serializers import serialize
import time


def home(request):
    return render(request, 'app/home.html' )

def post_item(request):
    if request.method == 'POST':
        form = Auction_Item_Form(request.POST, request.FILES)
        if form.is_valid:
            item = form.save(commit=False)
            item.price = item.startingbid
            item.start_time = timezone.now()
            duration = timedelta(minutes=2)
            item.end_time = item.start_time + duration
            item.save()

            return redirect('/auction_items')            
        else:
            return HttpResponse('Please try again to post your item')
    else:
        form = Auction_Item_Form()
    return render(request, 'app/post_item.html', {'form': form})

def auction_items(request):
    items = Auction_Item.objects.all()
    for item in items:
        if item.end_time <= timezone.now():
            item.status = 'closed'
            id = item.id
            last_bidder_name = get_last_bidder(id)
            item.winner = last_bidder_name

            file_path = f"auction_data_{id}.json"
            data = {
                'id': item.id,
                'product title': item.product_title,
                'product derscription': item.description,
                'start time': item.start_time,
                'end time': item.end_time,
                'start price': item.startingbid,
                'end price': item.price,
                'winner': item.winner,

            }
            json_string = json.dumps(data)
            hash = hashlib.sha256(json_string.encode("utf-8")).hexdigest()
            tx = sendTransaction(hash)
            item.txId = tx 

            with open(file_path, "w") as json_file:
                json.dump(json_string, json_file)
            item.save()
    items = Auction_Item.objects.filter(status='active')
    return render(request, 'app/auction_items.html', {'items': items})

def bid_form(request):
    form = BidForm()
    return render(request, 'bid.html', {'form': form})

def post_bid(request):
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            auction_id = form.cleaned_data['auction_id']
            bid_amount = form.cleaned_data['bid_amount']

            obj = Auction_Item.objects.get(pk=auction_id)
            # Check if the bid is higher than the starting price or the previous bid
            highest_bid = get_highest_bid(auction_id) 
            if bid_amount > highest_bid and bid_amount > obj.startingbid:
                obj.price = bid_amount
                obj.save()
                update = form.save(commit=False)
                update.save()
            else:
                return HttpResponseBadRequest('Your bid must be higher than the current highest bid.')

            #store the values in redis
            redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
            redis_key = f'auction:{auction_id}:bids'
            member = request.user.id
            score = bid_amount
            redis_client.zadd(redis_key, {member: score})

            return HttpResponse('Bid placed successfully.')
    else:
        form = BidForm()

    return render(request, 'app/bid.html', {'form': form})

def get_highest_bid(id):
    redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
    redis_key = f'auction:{id}:bids'
    highest_bid = redis_client.zrevrange(redis_key, 0, 0, withscores=True)
    if highest_bid:
        return float(highest_bid[0][1])
    return 0.0

#get the last bidder to assign the winner of each auction
def get_last_bidder(auction_id):
    redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
    redis_key = f'auction:{auction_id}:bids'

    last_bid = redis_client.zrevrange(redis_key, 0, 0, withscores=True)

    if last_bid:
        last_bidder_id, _ = last_bid[0]
        last_bidder = User.objects.get(id=last_bidder_id)
        return last_bidder.username
    else:
        return None

