from django.core.paginator import Paginator, EmptyPage
from ninja.errors import HttpError


class PaginationService:
    @staticmethod
    def paginate_queryset(queryset, page: int = 1, page_size: int = 20):
        paginator = Paginator(queryset, page_size)

        try:
            page_obj = paginator.page(page)
            return {
                'items': list(page_obj),
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_prev': page_obj.has_previous(),
            }
        except EmptyPage:
            raise HttpError(404, "Page not found")