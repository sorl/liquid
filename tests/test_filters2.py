# -*- coding: utf-8 -*-
"""
    jinja2.testsuite.filters
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for the jinja filters.

    :copyright: (c) 2010 by the Jinja Team.
    :license: BSD, see LICENSE for more details.
"""
import pytest
from jinja2 import Markup, Environment
from jinja2._compat import text_type, implements_to_string


@pytest.mark.filter2
class TestFilter2():
    def test_filter_calling(self, env):
        rv = env.call_filter('sum', [1, 2, 3])
        assert rv == 6

    def test_capitalize(self, env):
        tmpl = env.from_string('{{ "foo bar" | capitalize }}')
        assert tmpl.render() == 'Foo bar'

    def test_center(self, env):
        tmpl = env.from_string('{{ "foo" | center: 9 }}')
        assert tmpl.render() == '   foo   '

    def test_default(self, env):
        tmpl = env.from_string(
            "{{ missing | default: 'no' }}|{{ false | default: 'no' }}|"
            "{{ false|default: 'no', true }}|{{ given | default: 'no' }}"
        )
        assert tmpl.render(given='yes') == 'no|False|no|yes'

    def test_dictsort(self, env):
        tmpl = env.from_string(
            '{{ foo | dictsort }}|'
            '{{ foo | dictsort: true }}|'
            '{{ foo | dictsort: false, "value" }}'
        )
        out = tmpl.render(foo={"aa": 0, "b": 1, "c": 2, "AB": 3})
        assert out == ("[('aa', 0), ('AB', 3), ('b', 1), ('c', 2)]|"
                       "[('AB', 3), ('aa', 0), ('b', 1), ('c', 2)]|"
                       "[('aa', 0), ('b', 1), ('c', 2), ('AB', 3)]")

    def test_batch(self, env):
        tmpl = env.from_string("{{ foo | batch: 3 | list }}|"
                               "{{ foo | batch: 3, 'X' | list }}")
        out = tmpl.render(foo=list(range(10)))
        assert out == ("[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]|"
                       "[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 'X', 'X']]")

    def test_slice(self, env):
        tmpl = env.from_string('{{ foo | slice: 3 | list }}|'
                               '{{ foo | slice: 3, "X" | list }}')
        out = tmpl.render(foo=list(range(10)))
        assert out == ("[[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]|"
                       "[[0, 1, 2, 3], [4, 5, 6, 'X'], [7, 8, 9, 'X']]")

    def test_escape(self, env):
        tmpl = env.from_string('''{{ '<">&' | escape }}''')
        out = tmpl.render()
        assert out == '&lt;&#34;&gt;&amp;'

    def test_striptags(self, env):
        tmpl = env.from_string('''{{ foo | striptags }}''')
        out = tmpl.render(foo='  <p>just a small   \n <a href="#">'
                          'example</a> link</p>\n<p>to a webpage</p> '
                          '<!-- <p>and some commented stuff</p> -->')
        assert out == 'just a small example link to a webpage'

    def test_filesizeformat(self, env):
        tmpl = env.from_string(
            '{{ 100 | filesizeformat }}|'
            '{{ 1000 | filesizeformat }}|'
            '{{ 1000000 | filesizeformat }}|'
            '{{ 1000000000 | filesizeformat }}|'
            '{{ 1000000000000 | filesizeformat }}|'
            '{{ 100 | filesizeformat: true }}|'
            '{{ 1000 | filesizeformat: true }}|'
            '{{ 1000000 | filesizeformat: true }}|'
            '{{ 1000000000 | filesizeformat: true }}|'
            '{{ 1000000000000 | filesizeformat: true }}'
        )
        out = tmpl.render()
        assert out == (
            '100 Bytes|1.0 kB|1.0 MB|1.0 GB|1.0 TB|100 Bytes|'
            '1000 Bytes|976.6 KiB|953.7 MiB|931.3 GiB'
        )

    def test_filesizeformat_issue59(self, env):
        tmpl = env.from_string(
            '{{ 300 | filesizeformat }}|'
            '{{ 3000 | filesizeformat }}|'
            '{{ 3000000 | filesizeformat }}|'
            '{{ 3000000000 | filesizeformat }}|'
            '{{ 3000000000000 | filesizeformat }}|'
            '{{ 300 | filesizeformat: true }}|'
            '{{ 3000 | filesizeformat: true }}|'
            '{{ 3000000 | filesizeformat: true }}'
        )
        out = tmpl.render()
        assert out == (
            '300 Bytes|3.0 kB|3.0 MB|3.0 GB|3.0 TB|300 Bytes|'
            '2.9 KiB|2.9 MiB'
        )

    def test_first(self, env):
        tmpl = env.from_string('{{ foo | first }}')
        out = tmpl.render(foo=list(range(10)))
        assert out == '0'

    def test_float(self, env):
        tmpl = env.from_string('{{ "42" | float }}|'
                               '{{ "ajsghasjgd" | float }}|'
                               '{{ "32.32" | float }}')
        out = tmpl.render()
        assert out == '42.0|0.0|32.32'

    def test_format(self, env):
        tmpl = env.from_string('''{{ "%s|%s" | format:"a", "b" }}''')
        out = tmpl.render()
        assert out == 'a|b'

    def test_indent(self, env):
        tmpl = env.from_string('{{ foo | indent: 2 }}|{{ foo | indent: 2, true }}')
        text = '\n'.join([' '.join(['foo', 'bar'] * 2)] * 2)
        out = tmpl.render(foo=text)
        assert out == ('foo bar foo bar\n  foo bar foo bar|  '
                       'foo bar foo bar\n  foo bar foo bar')

    def test_int(self, env):
        class IntIsh(object):
            def __int__(self):
                return 42

        tmpl = env.from_string('{{ "42" | int }}|{{ "ajsghasjgd" | int }}|'
                               '{{ "32.32" | int }}|{{ "0x4d32" | int: 0, 16 }}|'
                               '{{ "011" | int: 0, 8 }}|{{ "0x33FU" | int: 0, 16 }}|'
                               '{{ obj | int }}')
        out = tmpl.render(obj=IntIsh())
        assert out == '42|0|32|19762|9|0|42'

    def test_join(self, env):
        tmpl = env.from_string('{{ [1, 2, 3] | join: "|" }}')
        out = tmpl.render()
        assert out == '1|2|3'

        env2 = Environment(autoescape=True)
        tmpl = env2.from_string(
            '{{ ["<foo>", "<span>foo</span>"|safe]|join }}')
        assert tmpl.render() == '&lt;foo&gt;<span>foo</span>'

    def test_join_attribute(self, env):
        class User(object):
            def __init__(self, username):
                self.username = username
        tmpl = env.from_string('''{{ users | join: ', ', 'username' }}''')
        assert tmpl.render(users=map(User, ['foo', 'bar'])) == 'foo, bar'

    def test_last(self, env):
        tmpl = env.from_string('''{{ foo | last }}''')
        out = tmpl.render(foo=list(range(10)))
        assert out == '9'

    def test_length(self, env):
        tmpl = env.from_string('''{{ "hello world" | length }}''')
        out = tmpl.render()
        assert out == '11'

    def test_lower(self, env):
        tmpl = env.from_string('''{{ "FOO" | lower }}''')
        out = tmpl.render()
        assert out == 'foo'

    def test_pprint(self, env):
        from pprint import pformat
        tmpl = env.from_string('''{{ data | pprint }}''')
        data = list(range(1000))
        assert tmpl.render(data=data) == pformat(data)

    def test_random(self, env):
        tmpl = env.from_string('''{{ seq | random }}''')
        seq = list(range(100))
        for _ in range(10):
            assert int(tmpl.render(seq=seq)) in seq

    def test_reverse(self, env):
        tmpl = env.from_string('{{ "foobar" | reverse | join }}|'
                               '{{ [1, 2, 3] | reverse | list }}')
        assert tmpl.render() == 'raboof|[3, 2, 1]'

    def test_string(self, env):
        x = [1, 2, 3, 4, 5]
        tmpl = env.from_string('''{{ obj | string }}''')
        assert tmpl.render(obj=x) == text_type(x)

    def test_title(self, env):
        tmpl = env.from_string('''{{ "foo bar" | title }}''')
        assert tmpl.render() == "Foo Bar"
        tmpl = env.from_string('''{{ "foo's bar" | title }}''')
        assert tmpl.render() == "Foo's Bar"
        tmpl = env.from_string('''{{ "foo   bar" | title }}''')
        assert tmpl.render() == "Foo   Bar"
        tmpl = env.from_string('''{{ "f bar f" | title }}''')
        assert tmpl.render() == "F Bar F"
        tmpl = env.from_string('''{{ "foo-bar" | title }}''')
        assert tmpl.render() == "Foo-Bar"
        tmpl = env.from_string('''{{ "foo\tbar" | title }}''')
        assert tmpl.render() == "Foo\tBar"
        tmpl = env.from_string('''{{ "FOO\tBAR" | title }}''')
        assert tmpl.render() == "Foo\tBar"
        tmpl = env.from_string('''{{ "foo (bar)" | title }}''')
        assert tmpl.render() == "Foo (Bar)"
        tmpl = env.from_string('''{{ "foo {bar}" | title }}''')
        assert tmpl.render() == "Foo {Bar}"
        tmpl = env.from_string('''{{ "foo [bar]" | title }}''')
        assert tmpl.render() == "Foo [Bar]"
        tmpl = env.from_string('''{{ "foo <bar>" | title }}''')
        assert tmpl.render() == "Foo <Bar>"

        class Foo:
            def __str__(self):
                return 'foo-bar'

        tmpl = env.from_string('''{{ data | title }}''')
        out = tmpl.render(data=Foo())
        assert out == 'Foo-Bar'

    def test_truncate(self, env):
        tmpl = env.from_string(
            '{{ data | truncate: 15, true, ">>>" }}|'
            '{{ data | truncate: 15, false, ">>>" }}|'
            '{{ smalldata | truncate: 15 }}'
        )
        out = tmpl.render(data='foobar baz bar' * 1000,
                          smalldata='foobar baz bar')
        msg = 'Current output: %s' % out
        assert out == 'foobar baz b>>>|foobar baz >>>|foobar baz bar', msg

    def test_truncate_very_short(self, env):
        tmpl = env.from_string(
            '{{ "foo bar baz" | truncate: 9 }}|'
            '{{ "foo bar baz" | truncate: 9, true }}'
        )
        out = tmpl.render()
        assert out == 'foo ...|foo ba...', out

    def test_truncate_end_length(self, env):
        tmpl = env.from_string('{{ "Joel is a slug" | truncate: 9, true }}')
        out = tmpl.render()
        assert out == 'Joel i...', 'Current output: %s' % out

    def test_upper(self, env):
        tmpl = env.from_string('{{ "foo" | upper }}')
        assert tmpl.render() == 'FOO'

    def test_urlize(self, env):
        tmpl = env.from_string(
            '{{ "foo http://www.example.com/ bar" | urlize }}')
        assert tmpl.render() == 'foo <a href="http://www.example.com/">'\
                                'http://www.example.com/</a> bar'

    def test_urlize_target_parameter(self, env):
        tmpl = env.from_string(
            '{{ "foo http://www.example.com/ bar" | urlize: target="_blank" }}'
        )
        assert tmpl.render() \
            == 'foo <a href="http://www.example.com/" target="_blank">'\
            'http://www.example.com/</a> bar'
        tmpl = env.from_string(
            '{{ "foo http://www.example.com/ bar" | urlize: target=42 }}'
        )
        assert tmpl.render() == 'foo <a href="http://www.example.com/">'\
                                'http://www.example.com/</a> bar'

    def test_wordcount(self, env):
        tmpl = env.from_string('{{ "foo bar baz" | wordcount }}')
        assert tmpl.render() == '3'

    def test_block(self, env):
        tmpl = env.from_string(
            '{% filter lower | escape %}<HEHE>{% endfilter %}'
        )
        assert tmpl.render() == '&lt;hehe&gt;'

    def test_chaining(self, env):
        tmpl = env.from_string(
            '''{{ ['<foo>', '<bar>'] | first | upper | escape }}'''
        )
        assert tmpl.render() == '&lt;FOO&gt;'

    def test_sum(self, env):
        tmpl = env.from_string('''{{ [1, 2, 3, 4, 5, 6] | sum }}''')
        assert tmpl.render() == '21'

    def test_sum_attributes(self, env):
        tmpl = env.from_string('''{{ values | sum: 'value' }}''')
        assert tmpl.render(values=[
            {'value': 23},
            {'value': 1},
            {'value': 18},
        ]) == '42'

    def test_sum_attributes_nested(self, env):
        tmpl = env.from_string('''{{ values | sum: 'real.value' }}''')
        assert tmpl.render(values=[
            {'real': {'value': 23}},
            {'real': {'value': 1}},
            {'real': {'value': 18}},
        ]) == '42'

    def test_sum_attributes_tuple(self, env):
        tmpl = env.from_string('''{{ values.items()|sum: '1' }}''')
        assert tmpl.render(values={
            'foo': 23,
            'bar': 1,
            'baz': 18,
        }) == '42'
