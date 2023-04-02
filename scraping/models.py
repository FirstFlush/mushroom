from datetime import date
from django.db import models


class Website(models.Model):

    domain = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.domain


class Cultivator(models.Model):

    website_id  = models.ForeignKey(to=Website, on_delete=models.CASCADE)
    name        = models.CharField(max_length=200)
    number      = models.IntegerField(unique=True)
    is_trusted  = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}  #{self.number}" 



class Post(models.Model):

    post_num        = models.IntegerField(unique=True)
    author_id       = models.ForeignKey(to=Cultivator, on_delete=models.CASCADE)
    thread_title    = models.CharField(max_length=150)
    body            = models.TextField(max_length=56300)
    date            = models.DateField()

    def body_head(self):
        return f"{self.body[:60]}....."

    def get_url(self):
        return f"https://www.shroomery.org/forums/showflat.php/Number/{self.post_num}#{self.post_num}"



