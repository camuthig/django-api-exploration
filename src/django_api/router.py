# Minimal decorator-based router to register Django views without internal type handling.
# This sketch provides a Router class with convenience decorators for common HTTP methods.
from typing import Callable
from typing import TypedDict

from django.http import HttpResponseNotAllowed
from django.views import View


class RouterPath(TypedDict):
    name: str
    funcs: dict[str, Callable]



class Router:
    """
    A lightweight router that lets you register Django views using decorator syntax.

    Example:
        router = Router()

        @router.get("items/")
        def list_items(request):
            return HttpResponse("items")

        urlpatterns = router.urls()
    """

    def __init__(self, name: str = None):
        # Internal storage of route definitions: list of dicts
        self._name = name
        self._routes: dict[str, RouterPath] = {}

    def _normalize_path(self, path):
        # Build a Django-friendly route path using the optional prefix
        # WIP This is possibly AI nonsense and needs review
        p = (path or "").strip("/")
        return p.rstrip().lstrip("/") + ("" if p.endswith("/") else "/")

    def _register(self, path: str, method: str):
        """
        Register a route with a decorator.
        path: URL path relative to the Router's prefix (e.g., "items/" or "items/<int:id>/")
        methods: iterable of HTTP method names, e.g. ["GET", "POST"]. Defaults to ["GET"].
        """
        path = self._normalize_path(path)
        if path not in self._routes:
            # WIP Come up with a way to convert the path to a name
            self._routes[path] = {"name": path.replace("/", "_"), "funcs": {}}

        router_path = self._routes[path]
        if method in router_path["funcs"]:
            raise ValueError(f"Method {method} already registered for path {path}")


        def decorator(view_func):
            router_path["funcs"][method] = view_func
            return view_func

        return decorator

    # Convenience decorators for common HTTP methods
    def get(self, path):
        return self._register(path, "GET")

    def post(self, path):
        return self._register(path, "POST")

    def put(self, path):
        return self._register(path, "PUT")

    def patch(self, path):
        return self._register(path, "PATCH")

    def delete(self, path):
        return self._register(path, "DELETE")

    def head(self, path):
        return self._register(path, "HEAD")

    def options(self, path):
        return self._register(path, "OPTIONS")

    def urls(self, name: str = None):
        # WIP need to figure out how to configure name
        return self._get_urls(), "router", name or self._name

    def add_view(self, path, methods: list[str], view_cls: type[View]):
        for method in methods:
            self._register(path, method)(view_cls.as_view())

    def _get_urls(self):
        """
        Convert registered routes into a list of Django URL patterns that can be used in urls.py.

        Returns:
            list: A list of django.urls.path() pattern objects.
        """
        from django.urls import path

        def make_wrapper(view_funcs: dict[str, Callable]):
            def wrapper(request, *args, **kwargs):
                view_func = view_funcs.get(request.method)
                if not view_func:
                    return HttpResponseNotAllowed(list(view_funcs.keys()))

                return view_func(request, *args, **kwargs)
            return wrapper

        patterns = []
        for p, route_path in self._routes.items():
            # WIP This "name" is not robust enough
            patterns.append(path(p, make_wrapper(route_path["funcs"]), name=route_path["name"]))

        return patterns