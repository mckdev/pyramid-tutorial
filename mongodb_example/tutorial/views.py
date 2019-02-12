import colander
import deform.widget
from bson.objectid import ObjectId
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config


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
        pages = list(self.request.db['pages'].find())
        return dict(pages=pages)

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

            # Form is valid. Write new page to database.
            pages = self.request.db.pages
            page_id = pages.insert_one(
                {'title': appstruct['title'],
                 'body': appstruct['body']}
            ).inserted_id

            # Now visit new page.
            url = self.request.route_url('wikipage_view', uid=page_id)
            return HTTPFound(url)

        return dict(form=form)

    @view_config(route_name='wikipage_view', renderer='wikipage_view.pt')
    def wikipage_view(self):
        uid = self.request.matchdict['uid']
        page = self.request.db.pages.find_one({'_id': ObjectId(uid)})
        if page is None:
            raise HTTPNotFound
        return dict(page=page)


    @view_config(route_name='wikipage_edit', renderer='wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = self.request.matchdict['uid']
        page = self.request.db.pages.find_one({'_id': ObjectId(uid)})
        if page is None:
            raise HTTPNotFound
        page_id = str(page['_id'])

        wiki_form = self.wiki_form
        wiki_form.buttons += (deform.Button(name='delete'),)

        if 'delete' in self.request.params:
            url = self.request.route_url('wikipage_delete', uid=page_id)

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
            self.request.db.pages.update_one(
                {'_id': page['_id']},
                {'$set': page},
                upsert=False)

            url = self.request.route_url('wikipage_view', uid=page_id)

            return HTTPFound(url)

        form = wiki_form.render(page)

        return dict(page=page, form=form)

    @view_config(route_name='wikipage_delete', renderer='wikipage_delete.pt')
    def wikipage_delete(self):
        uid = self.request.matchdict['uid']
        page = self.request.db.pages.find_one({'_id': ObjectId(uid)})
        if page is None:
            raise HTTPNotFound
        page_id = str(page['_id'])
        self.request.db.pages.delete_one({'_id': page['_id']})
        message = 'Deleted page %s.' % page_id
        return dict(message=message)
