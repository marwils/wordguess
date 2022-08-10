import pytest

from guessapp.models import Word, Wordlist


@pytest.mark.django_db
def test_filter_word_length():
    german = Wordlist.objects.create(name="German")
    german.words.create(word="abc")
    german.words.create(word="abcd")
    german.words.create(word="efgh")
    assert 1 == Word.objects.filter(word__length=3).count()
    assert 2 == Word.objects.filter(word__length=4).count()
