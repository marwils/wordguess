from django.db import models
from django.db.models import CharField
from django.db.models.functions import Length


CharField.register_lookup(Length, "length")


class Wordlist(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Word(models.Model):
    wordlist = models.ForeignKey(
        Wordlist, on_delete=models.CASCADE, related_name="words"
    )
    word = models.CharField(max_length=100)
    rating = models.IntegerField()
