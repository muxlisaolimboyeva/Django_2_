from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import OurFeaturedPost


# Create your views here.

def index(request):
    q = (request.GET.get("q") or "").strip()
    ourfeaturepost = OurFeaturedPost.objects.all().order_by("-date")

    if q:
        ourfeaturepost = ourfeaturepost.filter(
            Q(name__icontains=q) |
            Q(title__icontains=q)
        )

    paginator = Paginator(ourfeaturepost, 5)
    page_number = request.GET.get("page")
    ourfeaturepost = paginator.get_page(page_number)

    ctx = {
        "ourfeaturepost": ourfeaturepost,
        "q": q,
    }
    return render(request, "index.html", ctx)


def blog(request):
    return render(request, 'blog.html')
