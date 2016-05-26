from nose.tools import eq_, ok_

from ckan.config.middleware import CKANFlask
import ckan.plugins as plugins
import ckan.tests.helpers as helpers


class TestFlaskIRoutes(helpers.FunctionalTestBase):
    @classmethod
    def _find_flask_app(cls, test_app):
        '''Recursively search the wsgi stack until the flask_app is
        discovered.

        Relies on each layer of the stack having a reference to the app they
        wrap in either a .app attribute or .apps list.
        '''
        if isinstance(test_app, CKANFlask):
            return test_app

        try:
            app = test_app.apps['flask_app'].app
        except (AttributeError, KeyError):
            pass
        else:
            return cls._find_flask_app(app)

        try:
            app = test_app.app
        except AttributeError:
            print('No .app attribute. '
                  'Have all layers of the stack got '
                  'a reference to the app they wrap?')
        else:
            return cls._find_flask_app(app)

    def setup(self):
        self.app = helpers._get_test_app()
        flask_app = self._find_flask_app(self.app)

        # Install plugin and register its blueprint
        if not plugins.plugin_loaded('example_flask_iroutes'):
            plugins.load('example_flask_iroutes')
            plugin = plugins.get_plugin('example_flask_iroutes')
            flask_app.register_blueprint(plugin.get_blueprint(),
                                         prioritise_rules=True)

    def test_plugin_route(self):
        '''Test extension sets up a unique route.'''
        res = self.app.get('/hello_plugin')

        eq_('Hello World, this is served from an extension', res.body)

    def test_plugin_route_core_pylons_override(self):
        '''Test extension overrides pylons core route.'''
        res = self.app.get('/about')

        ok_('This is an about page served from an extention, overriding the pylons url.' in res.body)

    def test_plugin_route_core_flask_override(self):
        '''Test extension overrides flask core route.'''
        res = self.app.get('/hello')

        ok_('Hello World, this is served from an extension, overriding the flask url.' in res.body)

    def test_plugin_route_with_helper(self):
        '''
        Test extension rendering with a helper method that exists shouldn't
        cause error.
        '''
        res = self.app.get('/helper')

        ok_('Hello World, helper here: en' in res.body)

    def test_plugin_route_with_non_existent_helper(self):
        '''
        Test extension rendering with a helper method that doesn't exist
        causes server error.
        '''
        self.app.get('/helper_not_here', status=500)
