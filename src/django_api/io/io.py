from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from django_api.io.response import APIResponse


class Parser:
    # Note: These parsers should be replaced by the work proposed in DEP 0015 https://github.com/django/deps/pull/88
    content_type: str

    def parse(self, body: bytes):
        raise NotImplementedError()

class Renderer:
    content_type: str

    def render(self, data) -> bytes:
        raise NotImplementedError()

class Mapper:
    def from_primitives(self, primitives) -> Any:
        raise NotImplementedError()

    def to_primitives(self, model: Any) -> dict | list | str | int | float | bool | None:
        raise NotImplementedError()

class RequestSpec:
    def __init__(self, parser: Parser, mapper: Mapper | None = None):
        self.parser = parser
        self.mapper = mapper
        self.content_type = parser.content_type

class ResponseSpec:
    def __init__(self, renderer: Renderer, mapper: Mapper | None = None):
        self.renderer = renderer
        self.mapper = mapper
        self.content_type = renderer.content_type


class JSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        from django.db.models import QuerySet
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)


class JSONParser(Parser):
    content_type = "application/json"

    def parse(self, body: bytes):
        import json
        return json.loads(body)


class JSONRenderer(Renderer):
    content_type = "application/json"

    def render(self, data) -> bytes:
        import json
        return json.dumps(data, cls=JSONEncoder).encode("utf-8")


class IOException(Exception):
    pass


def protocol(request_spec: RequestSpec | None = None, response_spec: ResponseSpec | None = None):
    def decorate(fn):
        fn._router_schema = {"consumes": getattr(request_spec, "content_type", None),
                         "produces": getattr(response_spec, "content_type", None)}
        def wrapper(request, *args, **kwargs):
            # 1) parse + validate
            if request_spec and request.method in {"POST", "PUT", "PATCH"}:
                req_ct = (request.headers.get("Content-Type") or "").split(";")[0].strip()
                if req_ct != request_spec.content_type:
                    raise IOException(f"Expected {request_spec.content_type} but got {req_ct}")
                try:
                    primitives = request_spec.parser.parse(request.body)
                except Exception as ex:
                    # WIP I think the parse should define how this gets handled?
                    raise ex
                if request_spec.mapper:
                    try:
                        kwargs["data"] = request_spec.mapper.from_primitives(primitives)
                    except Exception as ex:
                        # WIP The adapter should return something that can be serialized
                        raise IOException(str(ex))
                else:
                    kwargs["data"] = primitives
            if request_spec and request.method == "GET" and request_spec.mapper:
                try:
                    kwargs["data"] = request_spec.mapper.from_primitives(request.GET.dict() or {})
                except Exception as ex:
                    # WIP The adapter should return something that can be serialized
                    raise IOException(str(ex))

            # 2) call
            result = fn(request, *args, **kwargs)

            # 3) map to primitives + render
            if not response_spec:
                return result  # primitives or caller-managed
            try:
                primitives = result
                if isinstance(result, APIResponse):
                    primitives = result.plain_content

                if response_spec.mapper:
                    primitives = response_spec.mapper.to_primitives(primitives)

                body = response_spec.renderer.render(primitives)

                if isinstance(result, APIResponse):
                    resp = result
                    resp.content = body
                    resp["Content-Type"] = response_spec.content_type
                else:
                    resp = HttpResponse(body, content_type=response_spec.content_type)

                return resp
            except Exception as ex:
                raise IOException(str(ex))
        return wrapper
    return decorate


def json_protocol(request: Mapper | None = None, response: Mapper | None = None):
    return protocol(
        request_spec=RequestSpec(parser=JSONParser(), mapper=request),
        response_spec=ResponseSpec(renderer=JSONRenderer(), mapper=response)
    )