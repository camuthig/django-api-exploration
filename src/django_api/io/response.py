from typing import Any

from django.http import HttpResponse


class APIResponse(HttpResponse):
    """
    A simple wrapper around HttpResponse that allows for using non-primitive types as content.

    This is especially useful to allow for creating a response with custom headers and returning a type that will be
    serialized by the adapter layer, like a QuerySet.

    The response cannot be sent directly, as the content is blank without the value going through the `io` layer where
    the internally stored content is converted to bytes and added back to the response object.

    If the underlying `content` is accessed directly before it is explicitly set, then an error will be raised.

    Example:
    def list_departments(request):
        response = APIResponse(Department.objects.all())
        response["X-Custom-Header"] = "Custom header value"

        return response
    """

    def __init__(self, content: Any, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plain_content = content
        self._rendered = False

    @property
    def content(self):
        if not self._rendered:
            raise RuntimeError("Response content has not been rendered yet.")

        return HttpResponse.content.fget(self)

    @content.setter
    def content(self, value):
        self._rendered = True

        HttpResponse.content.fset(self, value)
