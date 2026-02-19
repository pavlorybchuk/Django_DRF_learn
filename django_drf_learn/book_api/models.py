from django.db import models


class Book(models.Model):
    title = models.CharField(
        max_length=255,
    )
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()

    class Meta:
        unique_together = ["title", "author"]

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"
