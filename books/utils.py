from django.db.models import QuerySet


class FiltersToKwargs:
    def __init__(self, filters: dict = None):
        self.filters = filters or {}
        self.cleaned_filters = {}

    def __enter__(self):
        if self.filters == {}:
            return self.cleaned_filters

        for key, value in self.filters.items():
            if bool(value):

                try:
                    _ = iter(value)
                    key += "__in"
                except TypeError:
                    pass

                if isinstance(value, QuerySet):
                    value = list(value)

                self.cleaned_filters[key] = value

        return self.cleaned_filters

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.filters = {}
        self.cleaned_filters = {}