from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
    name = 'Maciej'
    return Response('<body><h1>Hello {}!</h1></body>'.format(name))


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_route('hello', '/')
    config.add_view(hello_world, route_name='hello')
    return config.make_wsgi_app()
