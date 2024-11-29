from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Book(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name="Название"
    )
    year = models.IntegerField(
        verbose_name="Год выпуска",
        validators=[MinValueValidator(1900)]
    )
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(verbose_name="Изображение")
    rating = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Рейтинг"
    )

    def __repr__(self):
        return f"{self.__class__}({self.title}, {self.year})"

    def __str__(self):
        return self.title