from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from django_api.io.response import APIResponse


class Parser:
    content_type: str
    def parse(self, body: bytes): ...

class Renderer:
    content_type: str
    def render(self, data) -> bytes: ...

class Adapter:
    def deserialize(self, primitives) -> Any: ...
    def serialize(self, model: Any) -> dict | list | str | int | float | bool | None: ...

class InputSpec:
    def __init__(self, parser: Parser, adapter: Adapter | None = None):
        self.parser = parser
        self.adapter = adapter
        self.content_type = parser.content_type

class OutputSpec:
    def __init__(self, renderer: Renderer, adapter: Adapter | None = None):
        self.renderer = renderer
        self.adapter = adapter
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

def io(input_spec: InputSpec | None = None, output_spec: OutputSpec | None = None):
    def decorate(fn):
        fn._router_io = {"consumes": getattr(input_spec, "content_type", None),
                         "produces": getattr(output_spec, "content_type", None)}
        def wrapper(request, *args, **kwargs):
            # 1) parse + validate
            if input_spec and request.method in {"POST", "PUT", "PATCH"}:
                req_ct = (request.headers.get("Content-Type") or "").split(";")[0].strip()
                if req_ct != input_spec.content_type:
                    raise IOException(f"Expected {input_spec.content_type} but got {req_ct}")
                try:
                    primitives = input_spec.parser.parse(request.body)
                except Exception as ex:
                    # WIP I think the parse should define how this gets handled?
                    raise ex
                if input_spec.adapter:
                    try:
                        kwargs["data"] = input_spec.adapter.deserialize(primitives)
                    except Exception as ex:
                        # WIP The adapter should return something that can be serialized
                        raise IOException(str(ex))
                else:
                    kwargs["data"] = primitives
            if input_spec and request.method == "GET" and input_spec.adapter:
                try:
                    kwargs["data"] = input_spec.adapter.deserialize(request.GET.dict() or {})
                except Exception as ex:
                    # WIP The adapter should return something that can be serialized
                    raise IOException(str(ex))

            # 2) call
            result = fn(request, *args, **kwargs)

            # 3) serialize + render
            if not output_spec:
                return result  # primitives or caller-managed
            try:
                primitives = result
                if isinstance(result, APIResponse):
                    primitives = result.plain_content

                if output_spec.adapter:
                    primitives = output_spec.adapter.serialize(primitives)

                body = output_spec.renderer.render(primitives)

                # WIP The developer should be able to specify specifics on the response as well
                if isinstance(result, APIResponse):
                    resp = result
                    resp.content = body
                    resp["Content-Type"] = output_spec.content_type
                else:
                    resp = HttpResponse(body, content_type=output_spec.content_type)

                return resp
            except Exception as ex:
                raise IOException(str(ex))
        return wrapper
    return decorate
