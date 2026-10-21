from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.contrib import admin
from .forms import TopBuyersForm
from django.db.models.functions import Coalesce


def top_buyer(request):
    buyer = (
        get_user_model().objects
        .annotate(movies_purchased=Sum('order__item__quantity'))
        .filter(movies_purchased__gt=0)
        .order_by('-movies_purchased', 'username')
        .first()
    )
    return render(request, 'top_buyer.html', {'buyer': buyer})

def top_buyers(request):
    form = TopBuyersForm(request.GET)
    buyers = (
        get_user_model().objects
        .annotate(movies_purchased=Coalesce(Sum('order__item__quantity'), 0))
        .order_by('-movies_purchased', 'username')
    )
    if form.is_valid() and form.cleaned_data['size']:
        buyers = buyers[:form.cleaned_data['size']]

    template_data = admin.site.each_context(request)
    template_data['form'] = form
    template_data['buyers'] = buyers

    return render(request, 'top_buyers.html', template_data)

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html', {'template_data': template_data})
