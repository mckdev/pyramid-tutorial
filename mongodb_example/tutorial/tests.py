import unittest

from pyramid import testing


def _init_testing_db():
    from pymongo import MongoClient
    client = MongoClient()
    db = client.test_database
    coll = db.pages
    pages = [
        {'title': 'Test Page 1', 'body': 'Toast body 1.'},
        {'title': 'Test Page 2', 'body': 'Toast body 2.'},
        {'title': 'Test Page 3', 'body': 'Toast body 3.'}

    ]
    coll.insert_many(pages)
    return client


class WikilViewTests(unittest.TestCase):
    def setUp(self):
        self.client = _init_testing_db()
        self.config = testing.setUp()

    def tearDown(self):
        self.client.drop_database('test_database')
        testing.tearDown()

    def test_wiki_view(self):
        from .views import WikiViews

        request = testing.DummyRequest(db=self.client.test_database)
        inst = WikiViews(request)
        response = inst.wiki_view()
        self.assertEqual(len(response['pages']), 3)


class WikiFunctionalTest(unittest.TestCase):
    def setUp(self):
        self.client = _init_testing_db()
        self.db = self.client.test_database
        from pyramid.paster import get_app
        app = get_app('testing.ini')
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        self.client.drop_database('test_database')
        testing.tearDown()

    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<title>Wiki: View</title>', res.body)
        self.assertIn(b'Test Page 1', res.body)

    def test_view_page(self):
        page = self.db.pages.find_one({'title': 'Test Page 1'})
        page_id = str(page['_id'])
        res = self.testapp.get('/%s' % page_id, status=200)
        self.assertIn(b'Toast body 1.', res.body)

    def test_add_page(self):
        res = self.testapp.get('/add', status=200)
        self.assertIn(b'<h1>Wiki Add/Edit</h1>', res.body)

    def test_post_wiki(self):
        self.testapp.post('/add', {
            'title': 'New Title',
            'body': '<p>New Body</p>',
            'submit': 'submit'
        }, status=302)

        page = self.db.pages.find_one({'title': 'New Title'})
        page_id = str(page['_id'])
        res = self.testapp.get('/%s' % page_id, status=200)
        self.assertIn(b'<h1>New Title</h1>', res.body)
        self.assertIn(b'<p>New Body</p>', res.body)

    def test_edit_wiki(self):
        page = self.db.pages.find_one({'title': 'Test Page 1'})
        page_id = str(page['_id'])

        self.testapp.post('/%s/edit' % page_id, {
            'title': 'Edited Title',
            'body': '<p>Edited Body</p>',
            'submit': 'submit'
        }, status=302)

        res = self.testapp.get('/%s' % page_id, status=200)
        self.assertIn(b'<h1>Edited Title</h1>', res.body)
        self.assertIn(b'<p>Edited Body</p>', res.body)

    def test_delete_page(self):
        page = self.db.pages.find_one({'title': 'Test Page 3'})
        page_id = str(page['_id'])
        res = self.testapp.get('/%s/delete' % page_id, status=200)
        self.assertIn(b'<p>Deleted page %b.</p>' % page_id.encode(), res.body)
        self.testapp.get('/%s/delete' % page_id, status=404)
        self.testapp.get('/%s' % page_id, status=404)
