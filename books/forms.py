from django import forms

from books.models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        exclude = ['created_at']

class FileUploadForm(forms.Form):
    file = forms.FileField()
