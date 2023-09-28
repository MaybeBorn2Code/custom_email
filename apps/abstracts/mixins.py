# Python
from typing import Any
import redis
import pickle

# DRF
from rest_framework.response import Response

# Django
from django.forms.models import ModelFormMetaclass
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse
from django.db.models.query import QuerySet
from django.template import (
    loader,
    Template,
)

class ObjectMixin:
    """ObjectMixin."""

    def get_object(
        self,
        queryset: QuerySet[Any],
        obj_id: str
    ) -> Any:
        obj: Any = None
        try:
            obj = queryset.get(id=obj_id)
        except Exception as exc:
            print(f'ERROR.ObjectMixin.get_object: {exc}')
            return None
        else:
            return obj


class ResponseMixin:
    """ResponseMixin."""

    def get_json_response(
        self,
        data: dict[str, Any],
        key_name: str = 'default',
        paginator: Any = None
    ) -> Response:

        if paginator:
            return paginator.get_paginated_response(
                data
            )
        return Response(
            {
                'data': {
                    key_name: data
                }
            }
        )


class RedisBinMixin:
    """Mixin to get and set binary data in redis."""

    redis_db = redis.Redis(db=0)

    @classmethod
    def get_data(cls, key: str) -> None:
        val = cls.redis_db.get(key)
        if not val:
            return None
        return pickle.loads(val)

    @classmethod
    def set_data(cls, key: str, data: Any):
        val = pickle.dumps(data)
        cls.redis_db.set(key, val)


class HttpResponseMixin:
    """Mixin from http handlers."""

    content_type = 'text/html'

    def get_http_response(
        self,
        request: WSGIRequest,
        template_name: str,
        context: dict = {}
    ) -> HttpResponse:
        
        template: Template =\
            loader.get_template(
                template_name
            )

        return HttpResponse(
            template.render(
                context=context,
                request=request
            ),
            content_type=self.content_type
        )

    def get_http_response_and_check_form(
        self,
        request,
        form: ModelFormMetaclass
    ) -> HttpResponse:
        form = self.form(request.POST)
        if not form.is_valid():
            return HttpResponse('not ok')
        form.save()
        return HttpResponse('ok')