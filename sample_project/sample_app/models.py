from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_authors(self):
        pass


class Author(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_country(self):
        pass

    def get_books(self):
        pass


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=255)
    popularity = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return "{}({})".format(self.title, self.author)

    def get_author(self):
        pass
