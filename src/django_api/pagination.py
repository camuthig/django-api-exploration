from django.db.models import QuerySet


class QuerySetLimitOffsetPaginator:
    def __init__(self, limit: int, offset: int, queryset: QuerySet):
        self.limit = limit
        self.offset = offset
        self.queryset = queryset

    def _get_items(self):
        if not hasattr(self, "_items"):
            self._items = list(self.queryset[self.offset:self.offset + self.limit + 1])

        return self._items

    @property
    def items(self) -> list:
        return self._get_items()[: self.limit]

    @property
    def has_more(self) -> bool:
        return len(self._get_items()) > self.limit