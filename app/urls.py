from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name= 'home'),
    path('post_item', views.post_item, name= 'post_item'),
    path('auction_items', views.auction_items, name= 'auction_items'),
    path('bid', views.post_bid, name= 'bid'),
]