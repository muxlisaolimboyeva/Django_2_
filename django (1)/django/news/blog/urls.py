from django.urls import path
from .views import index, blog, category, about, subscribe_views

urlpatterns = [
    path('', index, name='home'),
    path('blog/', blog, name='blog'),
    path('about/<int:id>/', about, name='about'),
    path('category/', category, name='category'),
    path('subscribe', subscribe_views, name='subscribe')
]

