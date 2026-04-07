from django.db import models

# Create your models here.


class OurFeaturedPost(models.Model):
    name = models.CharField(blank=True, max_length=20)
    date = models.DateField()
    title = models.TextField()
    image = models.ImageField(upload_to="OurFeaturedPost")

    def __str__(self):
        return self.name



