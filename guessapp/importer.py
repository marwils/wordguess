from collections import defaultdict
from guessapp.models import Wordlist


class WordlistImporter:
    def __init__(self, lines: set):
        self._wordlist_raters = defaultdict(WordlistRater)
        self.__readlines(lines)

    def __readlines(self, lines: set):
        for line in lines:
            word = line.strip()
            word_len = len(word)
            is_word = True

            for i in range(1, word_len):
                if word[i].isupper():
                    is_word = False
                    break

            if is_word:
                self._wordlist_raters[word_len].add(word.lower())

    def persist(self, name: str):
        wordlist = Wordlist.objects.create(name=name)
        for rater in self._wordlist_raters.values():
            for word in rater.words:
                wordlist.words.create(word=word, rating=rater.rate(word))
        wordlist.save()


class WordlistRater:
    def __init__(self):
        self.words = set()
        self._character_counts = defaultdict(int)

    def add(self, word: str):
        self.words.add(word)
        self.__add_to_char_count(word)

    def __add_to_char_count(self, word: str):
        for char in word:
            self._character_counts[char] += 1

    def rate(self, word: str) -> int:
        rating = 0
        for char in set(word):
            rating += self._character_counts[char]
        return rating
