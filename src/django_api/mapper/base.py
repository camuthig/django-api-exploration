import abc
from typing import TypeVar

from django.forms import BaseModelForm
from django.forms import ModelForm


class AbstractMapper(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def load(self, data: dict | list):
        """
        A function that receives a dictionary or list of Python primitive values, validates them, and loads them into
        the mapper as cleaned data.
        """
        ...

    @abc.abstractmethod
    def get_data(self) -> dict | list:
        """
        Return the cleaned data as a dictionary or list.
        """
        ...

    @abc.abstractmethod
    def dump(self, obj) -> dict | list:
        """
        Given a Python object, return a dictionary or list of Python primitive values representing the cleaned data.
        """
        ...

    @abc.abstractmethod
    def get_schema(self) -> dict:
        """
        Generate a JSON Schema for the data structure.
        """
        ...


class AbstractModelMapper(AbstractMapper, metaclass=abc.ABCMeta):
    def save(self, commit: bool = True):
        """
        Save the cleaned data to the database as a model instance.
        """
        ...

    def save_m2m(self):
        """
        Save the many-to-many fields of the model to the database.

        This must be called after `save(commit=False)` to ensure the related models are stored.
        """
        ...

    # WIP There are definitely more methods we need to implement, but we are starting
    #   with what we have here.

F = TypeVar("F", bound=BaseModelForm)

class FormMapper(AbstractMapper):
    def __init__(self, form: type[F] | None = None):
        # Allow subclasses to define an inner Meta with `form`
        meta_form = getattr(getattr(self, "Meta", None), "form", None)
        self.form_class: type[F] | None = form or meta_form
        if self.form_class is None:
            raise ValueError("FormMapper requires a form class via __init__(form=...) or Meta.form")


    def load(self, data):
        self._form = self.form_class(data)
        self._form.full_clean()

        if not self._form.is_valid():
            raise ValueError(self._form.errors)

    def dump(self, obj):
        f = self.form_class(obj)
        f.full_clean()
        return f.cleaned_data


    def get_data(self):
        return dict(self._form.cleaned_data)

    def get_schema(self):
        properties = {}
        required = []
        for name, field in self.form_class.fields.items():
            # WIP No, this isn't complete, but it is an example.
            properties[name] = {"type": "string"}
            if field.required:
                required.append(name)

        return {
            "type": "objects",
            "properties": properties,
            "required": required,
        }


class ModelFormMapper(FormMapper, AbstractModelMapper):
    def __init__(self, form_class: type[ModelForm] = None):
        super().__init__(form_class)

    def save(self, commit: bool = True):
        return self._form.save(commit=commit)

    def save_m2m(self):
        return self._form.save_m2m()

    def dump(self, obj):
        f = self.form_class(instance=obj)
        return f.initial

    @property
    def instance(self):
        return self._form.instance
