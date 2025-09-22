from typing import Any
from typing import TypeVar

from rest_framework import serializers

from django_api.io.io import Mapper


class DRFMapper(Mapper):
    def __init__(self, serializer: type[serializers.Serializer]):
        self.serializer = serializer

    def to_primitives(self, model: Any) -> dict | list | str | int | float | bool | None:
        return self.serializer(instance=model).data

    def from_primitives(self, primitives) -> Any:
        serializer = self.serializer(data=primitives)

        serializer.is_valid(raise_exception=True)

        return serializer


ReqModel = TypeVar("ReqModel", bound=serializers.Serializer)
RespModel = TypeVar("RespModel", bound=serializers.Serializer)


def json_schema(request: type[ReqModel] = None, response: type[RespModel] = None):
    from django_api.io import io
    input_spec = None
    if request:
        input_spec = io.RequestSpec(parser=io.JSONParser(), mapper=DRFMapper(request))

    output_spec = None
    if response:
        output_spec = io.ResponseSpec(renderer=io.JSONRenderer(), mapper=DRFMapper(response))

    return io.schema(request_spec=input_spec, response_spec=output_spec)