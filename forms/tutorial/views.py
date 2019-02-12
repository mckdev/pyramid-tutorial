import colander
import deform.widget

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

pages = {
    '100': dict(uid='100', title='Page 100', body='<em>100</em>'),
    '101': dict(uid='101', title='Page 101', body='<em>101</em>'),
    '102': dict(uid='102', title='Page 102', body='<em>102</em>')
}


class WikiPage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )


class WikiViews(object):
    def __init__(self, request):
        self.request = request

    @property
    def wiki_form(self):
        schema = WikiPage()
        return deform.Form(schema, buttons=('submit',))

    @property
    def reqts(self):
        return self.wiki_form.get_widget_resources()

    @view_config(route_name='wiki_view', renderer='wiki_view.pt')
    def wiki_view(self):
        return dict(pages=pages.values())

    @view_config(route_name='wikipage_add', renderer='wikipage_addedit.pt')
    def wikipage_add(self):
        form = self.wiki_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid.
                return dict(form=e.render())

            # Form is valid. Make a new identifier and add to list.
            try:
                last_uid = int(sorted(pages.keys())[-1])
                new_uid = str(last_uid + 1)
            except IndexError:
                new_uid = '100'
            pages[new_uid] = dict(
                uid=new_uid,
                title=appstruct['title'],
                body=appstruct['body']
            )

            # Now visit new page.
            url = self.request.route_url('wikipage_view', uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)

    @view_config(route_name='wikipage_view', renderer='wikipage_view.pt')
    def wikipage_view(self):
        try:
            uid = self.request.matchdict['uid']
            page = pages[uid]
            return dict(page=page)
        except KeyError:
            return HTTPNotFound()

    @view_config(route_name='wikipage_edit', renderer='wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = self.request.matchdict['uid']
        page = pages[uid]

        wiki_form = self.wiki_form
        wiki_form.buttons += (deform.Button(name='delete'),)

        if 'delete' in self.request.params:
            url = self.request.route_url('wikipage_delete', uid=page['uid'])

            return HTTPFound(url)

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(page=page, form=e.render())

            # Change the content and redirect to the view.
            page['title'] = appstruct['title']
            page['body'] = appstruct['body']

            url = self.request.route_url('wikipage_view', uid=page['uid'])

            return HTTPFound(url)

        form = wiki_form.render(page)

        return dict(page=page, form=form)

    @view_config(route_name='wikipage_delete', renderer='wikipage_delete.pt')
    def wikipage_delete(self):
        uid = self.request.matchdict['uid']
        try:
            del pages[uid]
            message = 'Deleted page %s.' % uid
            return dict(message=message)
        except KeyError:
            return HTTPNotFound()
