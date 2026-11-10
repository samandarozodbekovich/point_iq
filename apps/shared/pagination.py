from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


def paginate(view, request, queryset, serializer_class, **extra):
    """Paginate a queryset inside a custom list() and keep its extra keys.

    Returns a dict with count/next/previous/results plus anything passed in
    `extra`, so endpoints that already answer {"status": ..., "count": ...,
    "results": [...]} keep that shape and only gain next/previous.
    """
    paginator = StandardPagination()
    page = paginator.paginate_queryset(queryset, request, view=view)
    return {
        **extra,
        "count": paginator.page.paginator.count,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": serializer_class(page, many=True, context=view.get_serializer_context()).data,
    }
