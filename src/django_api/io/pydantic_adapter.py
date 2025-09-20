from typing import Any
from typing import TypeVar

from pydantic import BaseModel

from django_api.io.serdes import Adapter

BM = TypeVar("BM", bound=BaseModel)


class PydanticAdapter(Adapter):
    def __init__(self, model: type[BM]):
        self.model = model

    def deserialize(self, primitives) -> Any:
        # WIP Error handling here is important
        return self.model.model_validate(primitives)

    def serialize(self, model) -> dict | list | str | int | float | bool | None:
        # WIP Error handling here is important
        if not isinstance(model, self.model):
            model = self.model.model_validate(model)

        return model.model_dump()


ReqModel = TypeVar("ReqModel", bound=BaseModel)
RespModel = TypeVar("RespModel", bound=BaseModel)


def pydantic_io(request: type[ReqModel] = None, response: type[RespModel] = None):
    from django_api.io import serdes
    input_spec = None
    if request:
        input_spec = serdes.InputSpec(parser=serdes.JSONParser(), adapter=PydanticAdapter(request))

    output_spec = None
    if response:
        output_spec = serdes.OutputSpec(renderer=serdes.JSONRenderer(), adapter=PydanticAdapter(response))

    return serdes.io(input_spec=input_spec, output_spec=output_spec)