from django.contrib import admin
from .models import OurFeaturedPost, CategoriesAbout, Category


# Register your models here.


@admin.register(OurFeaturedPost)
class AboutPageAdmin(admin.ModelAdmin):
    exclude = ('views',)


admin.site.register(CategoriesAbout)
admin.site.register(Category)

