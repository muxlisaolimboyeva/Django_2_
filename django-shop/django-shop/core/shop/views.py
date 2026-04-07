from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product


# Create your views here.

def index(requests):
    return render(requests, 'index.html')


def _404(requests):
    return render(requests, '404.html')


def about(requests):
    return render(requests, 'about.html')


def blog_detail(requests):
    return render(requests, 'blog-detail.html')


def blog_grid(requests):
    return render(requests, 'blog-grid.html')


def contact(request):
    return render(request, 'contact.html')


def faq(request):
    return render(request, 'faq.html')


@login_required
def my_account(request):
    return render(request, 'my-account.html')


@login_required
def my_account_address(request):
    return render(request, 'my-account-address.html')


@login_required
def my_account_edit(request):
    return render(request, 'my-account-edit.html')


@login_required
def my_account_orders(request):
    return render(request, 'my-account-orders.html')


@login_required
def order_details(requests):
    return render(requests, 'order-details.html')


def privacy(requests):
    return render(requests, 'privacy.html')


def product_detail(requests, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    ctx = {
        "product": product,
        "images": product.images.all(),
        "specs": product.specs.all(),
        "colors": product.colors.all(),
        "reviews": product.reviews.filter(is_published=True),
    }
    return render(requests, 'product-detail.html', ctx)


def checkout(requests):
    return render(requests, 'checkout.html')


def product_thumbs(requests):
    return render(requests, 'product-thumbs-right.html')


def shop_cart(requests):
    return render(requests, 'shop-cart.html')


def shop_default(requests):
    return render(requests, 'shop-default.html')


def track_your_order(requests):
    return render(requests, 'track-your-order.html')


def wishlist(requests):
    return render(requests, 'wishlist.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('my_account')
        else:
            return redirect('/?login=1')


def register_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return redirect('/?login=1')

        User.objects.create_user(username=username, password=password)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('my_account')


def logout_user(request):
    logout(request)
    return redirect('home')
