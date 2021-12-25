import csv

from django.core.management import BaseCommand
from reviews.models.category import Category


class Command(BaseCommand):
    help = 'Load a category csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, 'rt') as f:
            reader = csv.reader(f, dialect='excel', delimiter=',')
            next(reader, None)  # skip the header
            for row in reader:
                Category.objects.create(
                    id=row[0],
                    name=row[1],
                    slug=row[2]
                )
