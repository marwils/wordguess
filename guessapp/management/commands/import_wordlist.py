import argparse
import time

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from guessapp.importer import WordlistImporter


class Command(BaseCommand):
    help = "Import word list file"

    def add_arguments(self, parser):
        parser.add_argument("name", nargs=1, type=str)
        parser.add_argument("filename", type=argparse.FileType("r", encoding="utf-8"))

    def handle(self, *args, **options):
        name = options["name"][0]
        content = options["filename"].read().splitlines()

        start_time = time.time()
        importer = WordlistImporter(content)
        try:
            persisted_count = importer.persist(name)
        except IntegrityError:
            self.stdout.write(f"A wordlist with the same name already exists: {name}")
            return

        elapsed_time = time.time() - start_time

        self.stdout.write(
            f"Successfully persisted {persisted_count} words in {elapsed_time} Seconds"
        )
