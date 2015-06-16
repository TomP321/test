from __future__ import unicode_literals

from django.core.urls import RegexPattern, Resolver, ResolverEndpoint, ResolverMatch, Resolver404
from django.core.urls.resolvers import BaseResolver
from django.test import SimpleTestCase, RequestFactory

from .decorators import inner_decorator, outer_decorator
from .views import class_based_view, empty_view


class ResolverMatchTests(SimpleTestCase):
    def get_resolver_match(self, **kwargs):
        defaults = {
            'func': empty_view,
            'args': (),
            'kwargs': {},
            'url_name': 'empty'
        }
        defaults.update(kwargs)
        return ResolverMatch(**defaults)

    def test_empty_namespaces(self):
        match = self.get_resolver_match()
        self.assertEqual(match.namespaces, [])
        self.assertEqual(match.namespace, '')
        self.assertEqual(match.app_names, [])
        self.assertEqual(match.app_name, '')

    def test_function_func_path(self):
        match = self.get_resolver_match()
        self.assertEqual(match._func_path, 'urls.views.empty_view')

    def test_class_func_path(self):
        match = self.get_resolver_match(func=class_based_view)
        self.assertEqual(match._func_path, 'urls.views.ViewClass')

    def test_decorators_reverse_order(self):
        match = self.get_resolver_match(decorators=[outer_decorator, inner_decorator])
        self.assertEqual(match.callback.decorated_by, 'outer')

    def test_decorated_update_wrapper(self):
        match = self.get_resolver_match(decorators=[outer_decorator, inner_decorator])
        self.assertEqual(match.callback.__doc__, empty_view.__doc__)
        self.assertEqual(match.callback.__module__, empty_view.__module__)
        self.assertEqual(match.callback.__name__, empty_view.__name__)

    def test_view_name_no_url_name(self):
        match = self.get_resolver_match(url_name=None)
        self.assertEqual(match.view_name, 'urls.views.empty_view')

    def test_view_name_with_url_name(self):
        match = self.get_resolver_match(url_name='empty')
        self.assertEqual(match.view_name, 'empty')

    def test_namespace(self):
        match = self.get_resolver_match(namespaces=['foo', None, 'bar'])
        self.assertEqual(match.namespaces, ['foo', 'bar'])
        self.assertEqual(match.namespace, 'foo:bar')

    def test_app_name(self):
        match = self.get_resolver_match(app_names=['foo', None, 'bar'])
        self.assertEqual(match.app_names, ['foo', 'bar'])
        self.assertEqual(match.app_name, 'foo:bar')

    def test_namespaced_view_name(self):
        match = self.get_resolver_match(namespaces=['foo', 'bar'])
        self.assertEqual(match.view_name, 'foo:bar:empty')

    def test_from_submatch(self):
        submatch = ResolverMatch(empty_view, (), {'arg1': 42}, 'url_name', ['app2', 'app3'], ['ns2', 'ns3'], None)
        match = ResolverMatch.from_submatch(submatch, (), {'arg2': 37}, 'app1', 'ns1', [outer_decorator])
        self.assertEqual(match.__class__, ResolverMatch)
        self.assertEqual(match.url_name, 'url_name')
        self.assertEqual(match.app_name, 'app1:app2:app3')
        self.assertEqual(match.namespace, 'ns1:ns2:ns3')
        self.assertEqual(match.decorators, [outer_decorator])
        self.assertEqual(match.view_name, 'ns1:ns2:ns3:url_name')
        self.assertEqual(match.func, empty_view)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {'arg1': 42, 'arg2': 37})

    def test_from_submatch_with_kwargs_no_inherited_args(self):
        submatch = ResolverMatch(
            empty_view, (42, 37), {}, 'url_name', ['app1', 'app2'],
            ['ns1', 'ns2'], [inner_decorator]
        )
        match = ResolverMatch.from_submatch(submatch, (), {'arg1': 42}, decorators=[outer_decorator])
        self.assertEqual(match.__class__, ResolverMatch)
        self.assertEqual(match.url_name, 'url_name')
        self.assertEqual(match.app_name, 'app1:app2')
        self.assertEqual(match.namespace, 'ns1:ns2')
        self.assertEqual(match.decorators, [outer_decorator, inner_decorator])
        self.assertEqual(match.view_name, 'ns1:ns2:url_name')
        self.assertEqual(match.func, empty_view)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {'arg1': 42})

    def test_from_submatch_ignored_args_inherited_kwargs(self):
        submatch = ResolverMatch(empty_view, (), {'arg1': 42}, 'url_name', decorators=[inner_decorator])
        match = ResolverMatch.from_submatch(submatch, (42, 37), {}, 'app1', 'ns1')
        self.assertEqual(match.__class__, ResolverMatch)
        self.assertEqual(match.url_name, 'url_name')
        self.assertEqual(match.app_name, 'app1')
        self.assertEqual(match.namespace, 'ns1')
        self.assertEqual(match.decorators, [inner_decorator])
        self.assertEqual(match.view_name, 'ns1:url_name')
        self.assertEqual(match.func, empty_view)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {'arg1': 42})


class ResolverTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super(ResolverTests, cls).setUpClass()
        cls.rf = RequestFactory()

    def test_match(self):
        constraints = [
            RegexPattern(r'^/'),
            RegexPattern(r'^test/'),
            RegexPattern(r'^(?P<pk>\d+)/$'),
        ]
        resolver = BaseResolver(constraints=constraints)
        url = '/test/42/'
        request = self.rf.get(url)
        expected = '', (), {'pk': '42'}
        self.assertEqual(resolver.match(url, request), expected)

    def test_no_match(self):
        constraints = [
            RegexPattern(r'^/'),
            RegexPattern(r'^test/'),
            RegexPattern(r'^(?P<pk>\d+)/$'),
        ]
        resolver = BaseResolver(constraints=constraints)
        url = '/no/match/'
        request = self.rf.get(url)
        with self.assertRaises(Resolver404):
            resolver.match(url, request)

    def test_empty_constraints_match(self):
        resolver = BaseResolver()
        url = '/test/42/'
        request = self.rf.get(url)
        expected = '/test/42/', (), {}
        self.assertEqual(resolver.match(url, request), expected)

    def test_resolve_to_view(self):
        constraints = [
            RegexPattern(r'^/'),
            RegexPattern(r'^test/$'),
        ]
        resolver = ResolverEndpoint(empty_view, 'empty-view', constraints=constraints)
        url = '/test/'
        request = self.rf.get(url)
        match = resolver.resolve(url, request)
        self.assertEqual(match.__class__, ResolverMatch)
        self.assertEqual(match.func, empty_view)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {})
        self.assertEqual(match.url_name, 'empty-view')

    def test_nested_resolvers(self):
        endpoint = ResolverEndpoint(empty_view, 'empty-view', constraints=[RegexPattern(r'^detail/$')])
        resolver = Resolver([('ns1', endpoint)], 'app1', constraints=[
            RegexPattern(r'^/'),
            RegexPattern(r'^(?P<pk>\d+)/'),
        ])
        url = '/42/detail/'
        request = self.rf.get(url)
        match = resolver.resolve(url, request)
        self.assertEqual(match.__class__, ResolverMatch)
        self.assertEqual(match.func, empty_view)
        self.assertEqual(match.args, ())
        self.assertEqual(match.kwargs, {'pk': '42'})
        self.assertEqual(match.url_name, 'empty-view')
        self.assertEqual(match.app_name, 'app1')
        self.assertEqual(match.namespace, 'ns1')
        self.assertEqual(match.view_name, 'ns1:empty-view')
