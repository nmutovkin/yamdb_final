import csv

from django.core.management import BaseCommand
from reviews.models.review import Review
from reviews.models.title import Title
from reviews.models.user import User


class Command(BaseCommand):
    help = 'Load a reviews csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, 'rt') as f:
            reader = csv.reader(f, dialect='excel', delimiter=',')
            next(reader, None)  # skip the header
            for row in reader:
                title = Title.objects.get(pk=row[1])
                author = User.objects.get(pk=row[3])
                Review.objects.create(
                    id=row[0],
                    title=title,
                    text=row[2],
                    author=author,
                    score=row[4],
                    pub_date=row[5]
                )
