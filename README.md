# Exploring Ideas Around APIs in Django

This project is my exploration into the concepts of building APIs with Django.

This is not a robust or complete solution. There are many work-in-progress (WIP) concepts throughout the project where
I obviously skipped doing some work to keep moving forward on the interfaces.

Conceptually, my goal is to create building blocks that can be pieced together by developers to create the experience
they are looking for. Once we have enough building blocks, Django may be able to create the "advised" way to build APIs
in the future.

I've also tried to make this as "plugable" as possible. I do think it creates a bit of noise to support that, but that
is probably the burden of building a framework.

I have two examples of writing function-based views with mappers using [Pydantic](src/functional/pydantic_views.py) and 
[DRF serializers](src/functional/drf_views.py). These are overly simplified but show the interface that I am exploring.

The bulk of the "Django" code is in the `django_api` package.

## Important Parts of an API Layer

These are my top-level thoughts on what makes a great API-first developer experience.

**Error rendering**

Error rendering at both the framework (Django) level and view levels should be defined to work within the context of
API's rendering mechanisms. The view-layer errors are usually easier to work with. Making 500s render properly requires
interacting with the `handler500` function, which is a step outside of the views. This may just require documentation
to explain how to use update Django's default handling to render correctly, unless there is a hook point I'm not yet
aware of to alter that.

**API Routing**

Most APIs these days want to be able to route based on the combination of the path and the HTTP verb. The existing
Django CBVs rely on path-only routing to register. Function-based views require if/else checks to match on the verb
explicitly. This works and is not too verbose. However, I believe the better developer experience lies in just a little
syntatic sugar to allow for engineers to split up function-based views by verbs and combine CBVs onto a single path.

We have seen this implemented in both DRF and Ninja, which leads me to believe that it is a crucial pattern to support.

**Parsing and Rendering**

Parsing is the idea of taking the HTTP request with bytes and converting it into Python primitives.
Parsing is already supported in Django and with [DEP 0015](https://github.com/django/deps/pull/88) we should see even
better support for parsing JSON in the future. This same concept should be a building block on which we proceed for APIs.

Rendering of API responses is less well supported in Django. We do have the `JsonReponse` which wraps `json.dumps` and
works well. There isn't an easily extensible point here, like for `Parser` that can be plugged in at a static level that
might help define the behaviors of an API up front (to support schema generation, for example).

**Primitive Mapping/Validation**

Similar to Django's `Form` layer, it is powerful for developers to define the structure of requests upfront. This also
provides for an initial validation layer for the request input. I believe this validation layer should be focused on
validating the shape of data and not dip into Django concepts too much. For example, validating relationships exist at
this layer can easily degrade into N+1 queries that are hard for the engineer to control. But validating that an integer
greather than 0 is provided, and could be a valid foriegn key ID, is a good idea.

On the flip side, defining a similar mapper layer for the responses can be powerful. Things like Ninja's `ModelSchema` and
DRF's `ModelSerializer` are examples of simple mappers making it easier for developers to rapidly iterate on APIs that
are coupled to the domain models, while the standard `Schema` and `Serializer` responses allow for me flexibility while
still supporting schema generation.

An important lesson I have learned here is that making the request mapping and response mapping explicitly separate is a
good idea.

**Pagination Ergonomics**

I call this out because paginating API responses is a common pattern. Nearly every "list" API should support pagination
by default, and making that easy for developers, is important. I think this falls under the "mapping" layer, but calling
out the specific use case of pagination within that layer is still worthwhile. 

An extra thought on pagination is that the common pagination patterns in Django core often do not work as well for APIs.
Especially as APIs get larger, as they often do, being able to separate out concepts like `count` to better support
cursor pagination is important.

**Response Object Manipulation**

An API response is not just the data in the body. Headers are often as important as the body. Our system should make it
easy for developers to manipulate the response object to add headers, set cookies, etc., while still using the mapping
and rendering layers.

**Schema Generation**

Generating the OpenAPI schema for an API can be very helpful. From this, documentation and clients can be generated
automatically. This support is seen in both DRF and Ninja, and even for teams building internal APIs, it is beneficial
to serve up some form of documentation.

**Authentication**

Authentication is a piece that is already supported in Django. Usually, this is accomplished with authentication middleware
added at the global level. However, both DRF and Ninja support authentication at the view/router/API level. I think this
pattern has appeared because a single Django application can serve up multiple APIs, each with their own authentication
requirements.

With this in mind, I believe it is important for a solution to support authentication at the API level.

**Permissions**

I think permissions can be a "solved" concept using Django's already built-in permissions decorators This solution does
not always work for everyone, but I don't know if there is a reason to make permissions a new concept. If the provided
permissions don't work for a developer, then creating their own paradigm supported by decorators is likely the best
approach for now.

## Routing

Routing is the first building block presented here in `django_api.routing`. The goal of routing is to make it possible
to define either function based or class based views to the same path based on URL routing. This is a concept tackled in
both DRF and Ninja, and meets API developers where they are. In the form-rendered-view paradigm, having a different path
for each view was standard, but most API developer are in the paradigm of having two paths: one for the list/create, and one
for the detail/update/delete. This is possible in Django using generic class based views as well as condition checking in
function based views. The condition checking appears to be a less well accepted pattern in the Python community and elsewhere, though.

The router is dead simple, though, and is meant to just handle the conversion of paths with verbs to a single API path.

It can be used with function or class based views. Although, the benefits with the generic class based view are fewer.


```python
from django.http import JsonResponse

from django_api.router import Router

router = Router()

@router.get("/stuff")
def get_stuff(request):
    return JsonResponse({"List": "stuff"})


@router.post("/stuff")
def post_stuff(request):
    return JsonResponse({"Post": 1})
```

Then you can register this router with the Django URL configuration as `router.urls()`

Class based views can also be registered.

```python
# Either of these patterns work
router.get("/departments")(StuffListView.as_view())
router.add_view("/departments", ["POST"], StuffCreateView)
```

The benefits in the class-based view are minimal at this time. However, I think there is a role for a top-level concept
similar to Ninja's `NinjaAPI` class where developers can define global concepts like middleware, authentication, and error
handling. I think these are often concepts that create less noise when configured at a global level, rather than per-view.

## Protocols

This example lands on the name `protocol` for defining the serialization and mapping layers of the data. There are notably
two parts to protocols so far: input and output, and each part handles the ideas parsing/rendering and
mapping to/from Python objects.

1. Parsing is already a concept that exists within Django and we can leverage that. The existing 
   [DEP 0015](https://github.com/django/deps/pull/88) is a great example of what already could exist in Django.
2. Rendering somewhat exists in Django and can be seen in things like `HttpResponse` and `JsonResponse`. However, I think
   we can formalize this a bit more and create `Renderer` concepts just like we already have `Parser` concepts.
3. Mapping is the idea of taking the parsed primitives and turning it into a Python object and back again for rendering.

Mapping is the part that I believe is the most controversial on the "right" approach. My attempt here is to create an
interface that allows for teams to bring in the tool they like the most: DRF serializers, Pydantic models, cattrs, or
even nothing. I have a couple of examples using [pydantic](src/functional/pydantic_views.py) and 
[DRF serializers](src/functional/drf_views.py) in this project.

My concern is that this layer is creating a decent bit of code. Most of that I was able to encapsulate away into the
decorators in the "easy" use cases, though, which I think is aligned with Django's core tenets. 

## Mising Pieces

### Router Aggregation

I think the idea of "router aggregation" is good. Grouping routes together into a concrete "API" concept allows for defining
multiple APIs in a single Django project with each having their own configurations. For example, there may be a "internal"
API used by a team's own applications and a "public" API that is used by external applications. These may use different
authentication methods or middleware. Additionally, the documentation for them will likely be served separately.

I think not implementing this yet is a reason for most of the other missing pieces as well.

### Django Layer

This project does not cover what it looks like to hook the behaviors into a more "Django sympathetic" layer. I owe that
exploration and have started seeing how the existing CBV views can be shifted to work well with the protocols.

I think the `Mapper` interfaces may need to include another method to support this, but I'm not yet sure what it looks
like. For transparency, I don't work with the existing sympathetic layer systems built into tools like DRF or
[Django Ninja CRUD](https://github.com/hbakri/django-ninja-crud) on my day-to-day, so I don't have very strong opinions
on what this should look like just yet. Just with the state of my project, I end up doing a lot of explicit transformations
that make those layers difficult to work with and not quite worth it.

### Error Handling

I tried exploring error handling as part of the `protocol` layer, but I think it is too noisy and hard to use. I think
a better approach would be to define it once at a top level `API` class that collects the `Router`s instead of per-view.

### Schema Generation

This is another concept that I think will benefit from me having router aggregation. The root of the routers will likely
define shared concepts like authentication, description, etc. and assist in generating the schema as a single document.

I think the protocol layer is where the actual schemas should come from. For example, you could introspect on the 
Mapper to generate these like with Pydantic or DRF serializers. We could add a `schema` concept explicitly to the protocol
layer as well, which would allow for developers to create their own methods, like returning out a plain file or dictionary
that manually defines the schema.

### Authentication

Right now, the examples would rely on whatever authentication mechanism is already configured by Django globally. I do
think this can work as a first pass at getting the building blocks together. However, I think there is a place in the
future for the router aggregation concept to control authentication at the API level.