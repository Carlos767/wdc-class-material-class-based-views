import csv

from django.db.models import Q
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from sample_app.models import Book, Author


class Command(BaseCommand):
    help = """
        Export all Books in Database into a CSV file. An `author_id` option
        can be sent in order to filter the books before exporting them.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--author_id', required=False,
            help='Export only books from author with given id')

    def handle(self, *args, **options):
        author_id = options.get('author_id')
        query = Q()
        if author_id:
            try:
                author = Author.objects.get(id=author_id)
            except Author.DoesNotExist:
                raise CommandError(
                    'Author with id {} does not exist.'.format(author_id))

            query = Q(author=author)

        books = Book.objects.filter(query)

        with open('{}/books.csv'.format(settings.BASE_DIR), 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Book ID',
                'Title',
                'Author',
                'Author ID',
                'ISBN',
                'Popularity'
            ])
            for book in books:
                writer.writerow([
                    book.id,
                    book.title,
                    book.author.name,
                    book.author.id,
                    book.isbn,
                    book.popularity,
                ])
