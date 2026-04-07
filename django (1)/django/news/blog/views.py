from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import render, get_object_or_404, redirect
from .models import OurFeaturedPost, CategoriesAbout, Category, PromoCode
from .utils import generate_promo_code


# Create your views here.

def index(request):
    q = (request.GET.get("q") or "").strip()

    ourfeaturedpost = OurFeaturedPost.objects.all().order_by("-date")

    if q:
        ourfeaturedpost = ourfeaturedpost.filter(
            Q(name__icontains=q) |
            Q(title__icontains=q) |
            Q(descriptions__icontains=q)
        )

    paginator = Paginator(ourfeaturedpost, 5)
    page_number = request.GET.get("page")
    ourfeaturedpost = paginator.get_page(page_number)

    ctx = {
        "ourfeaturedpost": ourfeaturedpost,
        "q": q
    }

    return render(request, 'index.html', ctx)


def blog(request):
    return render(request, 'blog.html')


def category(request):
    category_about = CategoriesAbout.objects.all()
    icategory = Category.objects.prefetch_related('categories_about')

    ctx = {
        "category_about": category_about,
        "icategory": icategory
    }
    return render(request, 'categories.html', ctx)


def about(request, id):
    about_post = get_object_or_404(OurFeaturedPost, id=id)

    OurFeaturedPost.objects.filter(id=id).update(views=F('views') + 1)
    about_post.refresh_from_db()

    ctx = {
        "post": about_post
    }
    return render(request, 'blog-details2.html', ctx)


def subscribe_views(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Email kiriting !")
            return redirect('/')

        code = generate_promo_code()
        PromoCode.objects.create(email=email, code=code)

        send_mail(
            subject="PROWEB hamjamiyatimizga qo'shiling 🥂",
            message=f"**PROWEB’da o‘qish uchun maxsus sovg‘a!\n\n"
                    f"🎉** Siz uchun **{code}** promo kodi orqali **20% chegirma** taqdim etiladi."
                    f"\nImkoniyatni qo‘ldan boy bermang va hoziroq ro‘yxatdan o‘ting!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Promo yuborildi !")
        return redirect('/')

