import time

from django.core.management.base import BaseCommand

from guessapp.models import Wordlist


class Command(BaseCommand):
    help = "Reads from db"

    def add_arguments(self, parser):
        parser.add_argument("wordlist", nargs=1, type=str)
        parser.add_argument("length", nargs=1, type=int)

    def handle(self, *args, **options):
        wordlist_name = options["wordlist"][0]
        word_length = options["length"][0]
        start_time = time.time()

        wordlist = Wordlist.objects.filter(name=wordlist_name).first()
        if not wordlist:
            self.stdout.write(f'Wordlist "{wordlist_name}" does not exist')
            return

        words = wordlist.words.filter(word__length=word_length).order_by("-rating")
        elapsed_time = time.time() - start_time

        self.stdout.write(
            f'Successfully filtered {words.count()} words in wordlist "{wordlist_name}" in {elapsed_time} seconds'
        )
