from typing import TypeVar

from django.db.models import ManyToManyField
from django.db.models import Model
from pydantic import BaseModel

from django_api.mapper.base import AbstractMapper

BM = TypeVar("BM", bound=BaseModel)


class PydanticMapper(AbstractMapper):
    def __init__(self, base_model: type[BM] | None = None):
        # Allow subclasses to define an inner Meta with `form`
        meta_base_model = getattr(getattr(self, "Meta", None), "base_model", None)
        self.base_model: type[BM] | None = base_model or meta_base_model
        if self.base_model is None:
            raise ValueError("PydanticMapper requires a base model class via __init__(base_model=...) or Meta.base_model")

    def load(self, data):
        self._model = self.base_model.model_validate(data)

    def get_data(self) -> dict | list:
        return self._model.model_dump()

    def dump(self, obj) -> dict | list:
        return self.base_model.model_validate(obj).model_dump()

    def get_schema(self) -> dict:
        return self.base_model.model_json_schema()


M = TypeVar("M", bound=Model)


class PydanticModelMapper(PydanticMapper):
    def __init__(self, model: type[BM] | None = None, base_model: type[BM] | None = None):
        super().__init__(base_model)
        self._instance = None
        self._m2m = {}

        meta_model = getattr(getattr(self, "Meta", None), "model", None)
        self.model: type[BM] | None = model or meta_model
        if self.model is None:
            raise ValueError("PydanticModelMapper requires a model class via __init__(model=...) or Meta.model")

    def save(self, commit: bool = True):
        # This code is pulled ad-hoc from Django Ninja CRUD as an example of what we could do.

        self._instance = self.model()
        for field, value in self._model.model_dump(exclude_unset=True).items():
            if isinstance(self._instance._meta.get_field(field), ManyToManyField):
                self._m2m[field] = value
            else:
                setattr(self._instance, field, value)

        if commit:
            self._instance.save()
            self.save_m2m()

    def save_m2m(self):
        for field, value in self._m2m.items():
            getattr(self._instance, field).set(value)

    @property
    def instance(self):
        return self._instance