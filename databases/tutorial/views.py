import colander
import deform.widget

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from .models import DBSession, Page


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
        pages = DBSession.query(Page).order_by(Page.title)
        return dict(title='Wiki View', pages=pages)

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

            # Form is valid. Add new page to database.
            new_title = appstruct['title']
            new_body = appstruct['body']
            DBSession.add(Page(title=new_title, body=new_body))

            # Get the new ID and redirect.
            page = DBSession.query(Page).filter_by(title=new_title).one()
            new_uid = page.uid

            url = self.request.route_url('wikipage_view', uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)

    @view_config(route_name='wikipage_view', renderer='wikipage_view.pt')
    def wikipage_view(self):
        uid = self.request.matchdict['uid']
        page = DBSession.query(Page).filter_by(uid=uid).one()
        return dict(page=page)

    @view_config(route_name='wikipage_edit', renderer='wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = self.request.matchdict['uid']
        page = DBSession.query(Page).filter_by(uid=uid).one()

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
            page.title = appstruct['title']
            page.body = appstruct['body']
            url = self.request.route_url('wikipage_view', uid=page['uid'])
            return HTTPFound(url)

        form = wiki_form.render(dict(
            uid=page.uid, title=page.title, body=page.body
        ))

        return dict(page=page, form=form)

    @view_config(route_name='wikipage_delete', renderer='wikipage_delete.pt')
    def wikipage_delete(self):
        uid = self.request.matchdict['uid']
        page = DBSession.query(Page).filter_by(uid=uid).one()
        DBSession.delete(page)
        message = 'Deleted page %s.' % uid
        return dict(message=message)
