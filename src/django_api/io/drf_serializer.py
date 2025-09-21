from typing import Any
from typing import TypeVar

from rest_framework import serializers

from django_api.io.serdes import Serializer


class DRFSerializer(Serializer):
    def __init__(self, serializer: type[serializers.Serializer]):
        self.serializer = serializer

    def serialize(self, model: Any) -> dict | list | str | int | float | bool | None:
        return self.serializer(instance=model).data

    def deserialize(self, primitives) -> Any:
        serializer = self.serializer(data=primitives)

        serializer.is_valid(raise_exception=True)

        return serializer


ReqModel = TypeVar("ReqModel", bound=serializers.Serializer)
RespModel = TypeVar("RespModel", bound=serializers.Serializer)


def drf_io(request: type[ReqModel] = None, response: type[RespModel] = None):
    from django_api.io import serdes
    input_spec = None
    if request:
        input_spec = serdes.RequestFormat(parser=serdes.JSONParser(), serializer=DRFSerializer(request))

    output_spec = None
    if response:
        output_spec = serdes.ResponseFormat(renderer=serdes.JSONRenderer(), deserializer=DRFSerializer(response))

    return serdes.io(input_spec=input_spec, output_spec=output_spec)