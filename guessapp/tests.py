from django.db import IntegrityError
import pytest
from guessapp.guesser import Guesser

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


def test_guesser_validate_wordlist_with_empty_wordlist():
    wordlist = []
    word_length = 0

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length).validate()
    assert e.value.args[0] == "Empty wordlist"


def test_guesser_validate_wordlist():
    wordlist = ["test"]
    word_length = 4

    Guesser(wordlist, word_length).validate()


def test_guesser_validate_word_length_with_too_small_length():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 0

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length).validate()
    assert e.value.args[0] == 'Unexpected length of word in wordlist: "abcde" with length of: 5'


def test_guesser_validate_word_length_with_too_high_length():
    wordlist = ["abcde", "cdefg", "efghi", "a"]
    word_length = 5

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length).validate()
    assert e.value.args[0] == 'Unexpected length of word in wordlist: "a" with length of: 1'


def test_guesser_validate_word_length():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5

    Guesser(wordlist, word_length).validate()


def test_guesser_validate_excluded_characters_without_item():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    excluded_characters = [None]

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, excluded_characters=excluded_characters).validate()
    assert e.value.args[0] == "Missing character in exluded_chars list"


def test_guesser_validate_excluded_characters_with_empty_string_item():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    excluded_characters = [""]

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, excluded_characters=excluded_characters).validate()
    assert e.value.args[0] == "Missing character in exluded_chars list"


def test_guesser_validate_excluded_characters_with_string_value():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    excluded_characters = ["ab"]

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, excluded_characters=excluded_characters).validate()
    assert e.value.args[0] == "Only one character per exclusion allowed in exluded_chars list"


def test_guesser_validate_excluded_characters():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    excluded_characters = ["a", "b"]

    Guesser(wordlist, word_length, excluded_characters=excluded_characters).validate()


def test_guesser_validate_safe_characters_without_character():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {None: 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == "Missing character in safe_characters dict"


def test_guesser_validate_safe_characters_with_empty_string_character():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"": 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == "Missing character in safe_characters dict"


def test_guesser_validate_safe_characters_with_too_much_characters():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"ab": 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == "Only one character per safe character allowed in safe_characters dict"


def test_guesser_validate_safe_characters_without_index():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"a": None}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == 'Missing index in safe_characters for character "a"'


def test_guesser_validate_safe_characters_with_bad_index_type():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"a": "abc"}

    with pytest.raises(TypeError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == 'Type of index is not integer of safe_characters character "a"'


def test_guesser_validate_safe_characters_with_too_low_index():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"a": -1}

    with pytest.raises(IndexError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == 'Index of safe character "a" out of bounds'


def test_guesser_validate_safe_characters_with_too_high_index():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"a": 5}

    with pytest.raises(IndexError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == 'Index of safe character "a" out of bounds'


def test_guesser_validate_safe_characters_with_two_characters_at_same_index():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"a": 1, "b": 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, safe_characters=safe_characters).validate()
    assert e.value.args[0] == 'Safe character "b" index is already reserved by "a"'


def test_guesser_validate_safe_characters():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    safe_characters = {"a": 1, "b": 2}

    Guesser(wordlist, word_length, safe_characters=safe_characters).validate()


def test_guesser_validate_characters_anywhere_without_character():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {None: 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == "Missing character in characters_anywhere dict"


def test_guesser_validate_characters_anywhere_with_empty_string_character():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"": 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == "Missing character in characters_anywhere dict"


def test_guesser_validate_characters_anywhere_with_too_much_characters():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"ab": 1}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == "Only one character per anywhere character allowed in characters_anywhere dict"


def test_guesser_validate_characters_anywhere_without_occurences():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"a": None}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == 'No occurences defined in safe_characters for character "a"'


def test_guesser_validate_characters_anywhere_with_bad_occurences_type():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"a": "abc"}

    with pytest.raises(TypeError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == 'Type of amount of occurences is not integer of safe_characters character "a"'


def test_guesser_validate_characters_anywhere_with_too_less_occurences():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"a": 0}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == 'Occurences of anywhere character "a" have to be at least 1'


def test_guesser_validate_characters_anywhere_with_too_much_occurences():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"a": 6}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()
    assert e.value.args[0] == 'Occurences of anywhere character "a" cannot exceed the amount of word character count 5'


def test_guesser_validate_characters_anywhere():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_anywhere = {"a": 1}

    Guesser(wordlist, word_length, characters_anywhere=characters_anywhere).validate()


def test_guesser_validate_characters_excluded_at_without_character():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {None: [1]}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == "Missing character in characters_excluded_at dict"


def test_guesser_validate_characters_excluded_at_with_empty_string_character():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"": [1]}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == "Missing character in characters_excluded_at dict"


def test_guesser_validate_characters_excluded_at_with_too_much_characters():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"ab": [1]}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == "Only one character per exclusion allowed in characters_excluded_at dict"


def test_guesser_validate_characters_excluded_at_with_empty_list():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": []}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == 'Missing list of indices for characters_excluded_at character "a"'


def test_guesser_validate_characters_excluded_at_with_bad_indices_type():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": "abc"}

    with pytest.raises(TypeError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == 'Type of indices for characters_excluded_at is not list for character "a"'


def test_guesser_validate_characters_excluded_at_with_missing_index_value():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": [None]}

    with pytest.raises(ValueError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == 'Missing index for characters_excluded_at character "a"'


def test_guesser_validate_characters_excluded_at_with_bad_index_type():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": ["a"]}

    with pytest.raises(TypeError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == 'Type of index for characters_excluded_at is not integer for character "a"'


def test_guesser_validate_characters_excluded_at_with_too_low_index():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": [-1]}

    with pytest.raises(IndexError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == 'Index of characters_excluded_at character "a" out of bounds'


def test_guesser_validate_characters_excluded_at_with_too_high_index():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": [5]}

    with pytest.raises(IndexError) as e:
        Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
    assert e.value.args[0] == 'Index of characters_excluded_at character "a" out of bounds'


def test_guesser_validate_characters_excluded_at():
    wordlist = ["abcde", "cdefg", "efghi"]
    word_length = 5
    characters_excluded_at = {"a": [0]}

    Guesser(wordlist, word_length, characters_excluded_at=characters_excluded_at).validate()
