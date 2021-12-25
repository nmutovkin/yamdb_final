import csv

from django.core.management import BaseCommand
from reviews.models.category import Category
from reviews.models.title import Title


class Command(BaseCommand):
    help = 'Load a title csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)
        parser.add_argument('--path2', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        path2 = kwargs['path2']
        with open(path, 'rt') as f:
            reader = csv.reader(f, dialect='excel', delimiter=',')
            next(reader, None)  # skip the header
            for row in reader:
                category = Category.objects.get(pk=row[3])
                Title.objects.create(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category=category
                )

        with open(path2, 'rt') as f:
            reader = csv.reader(f, dialect='excel', delimiter=',')
            next(reader, None)  # skip the header

            for row in reader:
                title = Title.objects.get(pk=row[1])
                title.genre.add(row[2])
