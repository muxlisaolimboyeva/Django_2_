from django.db import models
from django.utils.text import slugify


# Create your models here.

class Category(models.Model):
    text = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, null=True)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.text)
        super(Category, self).save(*args, **kwargs)


class OurFeaturedPost(models.Model):
    name = models.CharField(blank=True, max_length=20)
    title = models.TextField()
    descriptions = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to="OurFeaturedPost")

    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class CategoriesAbout(models.Model):
    title = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories_about')
    descriptions = models.TextField()
    date = models.DateField()
    name = models.CharField(blank=True, max_length=20)
    image = models.ImageField(upload_to="CategoriesAbout")

    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=20, unique=True)
    is_used = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.code}"
