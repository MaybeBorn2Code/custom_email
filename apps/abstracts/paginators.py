# DRF
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
)
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnList


class AbstractPageNumberPagination(PageNumberPagination):
    """My AbstractPageNumberPagination."""

    page_size_query_param: str = 'size'
    page_query_param: str = 'page'
    # макс.кол объектов (игнор параметра в url)
    max_page_size: int = 10
    # сколько объектов на страницу
    page_size: int = 2

    def get_paginated_response(self, data: ReturnList) -> Response:

        response: Response = \
            Response(
                {
                    'pagination': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link(),
                        'count': self.page.paginator.num_pages
                    },
                    'results': data
                }
            )
        return response


class AbstractLimitOffsetPagination(LimitOffsetPagination):
    """AbstractLimitOffsetPagination."""

    offset: int = 0
    limit: int = 2

    def get_paginated_response(
        self,
        data: ReturnList
    ) -> Response:
        response: Response = \
            Response(
                {
                    'pagination': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link()
                    },
                    'results': data
                }
            )
        return response
