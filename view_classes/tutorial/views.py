from pyramid.view import (
    view_config,
    view_defaults
)


@view_defaults(renderer='home.pt')
class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='home.pt')
    def home(self):
        return {'name': 'Home View'}

    @view_config(route_name='hello', renderer='home.pt')
    def hello(self):
        return {'name': 'Hello View'}
