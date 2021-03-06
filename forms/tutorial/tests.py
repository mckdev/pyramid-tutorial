import unittest

from pyramid import testing


class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_home(self):
        from .views import WikiViews

        request = testing.DummyRequest()
        inst = WikiViews(request)
        response = inst.wiki_view()
        self.assertEqual(len(response['pages']), 3)


class TutorialFunctionalTest(unittest.TestCase):
    def setUp(self):
        from tutorial import main

        app = main({})
        from webtest import TestApp

        self.testapp = TestApp(app)

    def tearDown(self):
        testing.tearDown()

    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<title>Wiki: View</title>', res.body)

    def test_add_page(self):
        res = self.testapp.get('/add', status=200)
        self.assertIn(b'<h1>Wiki</h1>', res.body)

    def test_edit_page(self):
        res = self.testapp.get('/101/edit', status=200)
        self.assertIn(b'<h1>Wiki</h1>', res.body)

    def test_post_wiki(self):
        self.testapp.post('/add', {
            'title': 'New Title',
            'body': '<p>New Body</p>',
            'submit': 'submit'
        }, status=302)

        res = self.testapp.get('/103', status=200)
        self.assertIn(b'<h1>New Title</h1>', res.body)
        self.assertIn(b'<p>New Body</p>', res.body)

    def test_edit_wiki(self):
        self.testapp.post('/102/edit', {
            'title': 'Edited Title',
            'body': '<p>Edited Body</p>',
            'submit': 'submit'
        }, status=302)

        res = self.testapp.get('/102', status=200)
        self.assertIn(b'<h1>Edited Title</h1>', res.body)
        self.assertIn(b'<p>Edited Body</p>', res.body)

    def test_delete_page(self):
        res = self.testapp.get('/100/delete', status=200)
        self.assertIn(b'<p>Deleted page 100.</p>', res.body)
        self.testapp.get('/100', status=404)

        self.testapp.get('/303/delete', status=404)
