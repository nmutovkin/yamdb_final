import csv

from django.core.management import BaseCommand
from reviews.models.comment import Comment
from reviews.models.review import Review
from reviews.models.user import User


class Command(BaseCommand):
    help = 'Load a comments csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, 'rt') as f:
            reader = csv.reader(f, dialect='excel', delimiter=',')
            next(reader, None)  # skip the header
            for row in reader:
                review = Review.objects.get(pk=row[1])
                author = User.objects.get(pk=row[3])
                Comment.objects.create(
                    id=row[0],
                    review=review,
                    text=row[2],
                    author=author,
                    pub_date=row[4]
                )
