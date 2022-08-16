from django.db import IntegrityError
import pytest

from guessapp.importer import WordlistImporter
from guessapp.models import Word, Wordlist


@pytest.mark.django_db
def test_filter_word_length():
    german = Wordlist.objects.create(name="German")
    german.words.create(word="abc", rating=6)
    german.words.create(word="abcd", rating=7)
    german.words.create(word="efgh", rating=4)
    assert 1 == Word.objects.filter(word__length=3).count()
    assert 2 == Word.objects.filter(word__length=4).count()


@pytest.mark.django_db
def test_importer():
    lines = ["abc", "def", "abcdefghi", "ghi", "feg", "leg", "jklmnopqr", "abcjklstu"]
    importer = WordlistImporter(lines)
    persisted_count = importer.persist("Test words")

    assert Word.objects.count() == len(lines)
    assert persisted_count == len(lines)

    word = Word.objects.filter(word__length=3).order_by("-rating").first().word
    assert word == "feg"

    word = Word.objects.filter(word__length=9).order_by("-rating").first().word
    assert word == "abcjklstu"

    with pytest.raises(IntegrityError):
        importer.persist("Test words")
