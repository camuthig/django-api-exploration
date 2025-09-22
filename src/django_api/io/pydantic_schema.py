from typing import Any
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from django_api.io.io import Mapper

BM = TypeVar("BM", bound=BaseModel)


class PydanticMapper(Mapper):
    def __init__(self, model: type[BM]):
        self.model = model

    def from_primitives(self, primitives) -> Any:
        # WIP Error handling here is important
        return self.model.model_validate(primitives)

    def to_primitives(self, model) -> dict | list | str | int | float | bool | None:
        # WIP Error handling here is important
        if not isinstance(model, self.model):
            model = self.model.model_validate(model)

        return model.model_dump()


PaginatedModel = TypeVar("PaginatedModel", bound=BaseModel)


class LimitOffsetPaginationModel[PaginatedModel](BaseModel):
    items: list[PaginatedModel]
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)
    has_more: bool

    model_config = ConfigDict(from_attributes=True)


class LimitOffsetPaginationQueryModel(BaseModel):
    limit: int = Field(10, ge=1)
    offset: int = Field(0, ge=0)


ReqModel = TypeVar("ReqModel", bound=BaseModel)
RespModel = TypeVar("RespModel", bound=BaseModel)


def json_schema(request: type[ReqModel] = None, response: type[RespModel] = None):
    from django_api.io import io
    input_spec = None
    if request:
        input_spec = io.RequestSpec(parser=io.JSONParser(), mapper=PydanticMapper(request))

    output_spec = None
    if response:
        output_spec = io.ResponseSpec(renderer=io.JSONRenderer(), mapper=PydanticMapper(response))

    return io.schema(request_spec=input_spec, response_spec=output_spec)