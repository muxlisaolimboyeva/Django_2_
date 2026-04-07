from django.urls import path
from .views import (index, _404, about, blog_detail, blog_grid, checkout, contact, faq, my_account, my_account_address,
                    my_account_edit,
                    my_account_orders, order_details, privacy, product_thumbs, shop_cart, shop_default,
                    track_your_order, wishlist, login_user, logout_user, register_user)

urlpatterns = [
    path('', index, name='home'),
    path('404/', _404, name='404'),
    path('about/', about, name='about'),
    path('blog/', blog_detail, name='blog_detail'),
    path('blog/grid/', blog_grid, name='blog_grid'),
    path('blog/checkout/', checkout, name='checkout'),
    path('contact/', contact, name='contact'),
    path('faq/', faq, name='faq'),
    path('my_account_address/', my_account_address, name='my_account_address'),
    path('my_account_edit/', my_account_edit, name='my_account_edit'),
    path('my_account_orders/', my_account_orders, name='my_account_orders'),
    path('order_details/', order_details, name='order_details'),
    path('privacy/', privacy, name='privacy'),
    path('product_thumbs/', product_thumbs, name='product_thumbs'),
    path('shop_cart/', shop_cart, name='shop_cart'),
    path('shop_default/', shop_default, name='shop_default'),
    path('track_your_order/', track_your_order, name='track_your_order'),
    path('wishlist/', wishlist, name='wishlist'),

    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('register/', register_user, name='register_user'),
    path('my_account/', my_account, name='my_account'),
]


