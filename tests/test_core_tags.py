# -*- coding: utf-8 -*-
"""
    jinja2.testsuite.core_tags
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the core tags like for and if.

    :copyright: (c) 2010 by the Jinja Team.
    :license: BSD, see LICENSE for more details.
"""
import pytest
from jinja2 import Environment, TemplateSyntaxError, UndefinedError, \
     DictLoader


@pytest.fixture
def env_trim():
    return Environment(trim_blocks=True)


@pytest.mark.core_tags
@pytest.mark.for_loop
class TestForLoop():

    def test_simple(self, env):
        tmpl = env.from_string('{% for item in seq %}{{ item }}{% endfor %}')
        assert tmpl.render(seq=list(range(10))) == '0123456789'

    def test_else(self, env):
        tmpl = env.from_string(
            '{% for item in seq %}XXX{% else %}...{% endfor %}')
        assert tmpl.render() == '...'

    def test_empty_blocks(self, env):
        tmpl = env.from_string('<{% for item in seq %}{% else %}{% endfor %}>')
        assert tmpl.render() == '<>'

    def test_context_vars(self, env):
        slist = [42, 24]
        for seq in [slist, iter(slist), reversed(slist), (_ for _ in slist)]:
            tmpl = env.from_string('''{% for item in seq -%}
            {{ forloop.index }}|{{ forloop.index0 }}|{{ forloop.rindex }}|{{
                forloop.rindex0 }}|{{ forloop.first }}|{{ forloop.last }}|{{
               forloop.length }}###{% endfor %}''')
            one, two, _ = tmpl.render(seq=seq).split('###')
            (one_index, one_index0, one_rindex, one_rindex0, one_first,
             one_last, one_length) = one.split('|')
            (two_index, two_index0, two_rindex, two_rindex0, two_first,
             two_last, two_length) = two.split('|')

            assert int(one_index) == 1 and int(two_index) == 2
            assert int(one_index0) == 0 and int(two_index0) == 1
            assert int(one_rindex) == 2 and int(two_rindex) == 1
            assert int(one_rindex0) == 1 and int(two_rindex0) == 0
            assert one_first == 'True' and two_first == 'False'
            assert one_last == 'False' and two_last == 'True'
            assert one_length == two_length == '2'

    def test_cycling(self, env):
        tmpl = env.from_string('''{% for item in seq %}{{
            forloop.cycle('<1>', '<2>') }}{% endfor %}{%
            for item in seq %}{{ forloop.cycle(*through) }}{% endfor %}''')
        output = tmpl.render(seq=list(range(4)), through=('<1>', '<2>'))
        assert output == '<1><2>' * 4

    def test_scope(self, env):
        tmpl = env.from_string('{% for item in seq %}{% endfor %}{{ item }}')
        output = tmpl.render(seq=list(range(10)))
        assert not output

    def test_varlen(self, env):
        def inner():
            for item in range(5):
                yield item
        tmpl = env.from_string('{% for item in iter %}{{ item }}{% endfor %}')
        output = tmpl.render(iter=inner())
        assert output == '01234'

    def test_noniter(self, env):
        tmpl = env.from_string('{% for item in none %}...{% endfor %}')
        pytest.raises(TypeError, tmpl.render)

    def test_recursive(self, env):
        tmpl = env.from_string('''{% for item in seq recursive -%}
            [{{ item.a }}{% if item.b %}<{{ forloop(item.b) }}>{% endif %}]
        {%- endfor %}''')
        assert tmpl.render(seq=[
            dict(a=1, b=[dict(a=1), dict(a=2)]),
            dict(a=2, b=[dict(a=1), dict(a=2)]),
            dict(a=3, b=[dict(a='a')])
        ]) == '[1<[1][2]>][2<[1][2]>][3<[a]>]'

    def test_recursive_depth0(self, env):
        tmpl = env.from_string('''{% for item in seq recursive -%}
            [{{ forloop.depth0 }}:{{ item.a }}{% if item.b %}<{{ forloop(item.b) }}>{% endif %}]
        {%- endfor %}''')
        assert tmpl.render(seq=[
            dict(a=1, b=[dict(a=1), dict(a=2)]),
            dict(a=2, b=[dict(a=1), dict(a=2)]),
            dict(a=3, b=[dict(a='a')])
        ]) == '[0:1<[1:1][1:2]>][0:2<[1:1][1:2]>][0:3<[1:a]>]'

    def test_recursive_depth(self, env):
        tmpl = env.from_string('''{% for item in seq recursive -%}
            [{{ forloop.depth }}:{{ item.a }}{% if item.b %}<{{ forloop(item.b) }}>{% endif %}]
        {%- endfor %}''')
        assert tmpl.render(seq=[
            dict(a=1, b=[dict(a=1), dict(a=2)]),
            dict(a=2, b=[dict(a=1), dict(a=2)]),
            dict(a=3, b=[dict(a='a')])
        ]) == '[1:1<[2:1][2:2]>][1:2<[2:1][2:2]>][1:3<[2:a]>]'

    def test_looploop(self, env):
        tmpl = env.from_string('''{% for row in table %}
            {%- set rowloop = forloop -%}
            {% for cell in row -%}
                [{{ rowloop.index }}|{{ forloop.index }}]
            {%- endfor %}
        {%- endfor %}''')
        assert tmpl.render(table=['ab', 'cd']) == '[1|1][1|2][2|1][2|2]'

    def test_reversed_bug(self, env):
        tmpl = env.from_string('{% for i in items %}{{ i }}'
                               '{% if not forloop.last %}'
                               ',{% endif %}{% endfor %}')
        assert tmpl.render(items=reversed([3, 2, 1])) == '1,2,3'

    def test_loop_errors(self, env):
        tmpl = env.from_string('''{% for item in [1] if forloop.index
                                      == 0 %}...{% endfor %}''')
        pytest.raises(UndefinedError, tmpl.render)
        tmpl = env.from_string('''{% for item in [] %}...{% else
            %}{{ forloop }}{% endfor %}''')
        assert tmpl.render() == ''

    def test_loop_filter(self, env):
        tmpl = env.from_string('{% for item in range(10) if item '
                               'is even %}[{{ item }}]{% endfor %}')
        assert tmpl.render() == '[0][2][4][6][8]'
        tmpl = env.from_string('''
            {%- for item in range(10) if item is even %}[{{
                forloop.index }}:{{ item }}]{% endfor %}''')
        assert tmpl.render() == '[1:0][2:2][3:4][4:6][5:8]'

    def test_loop_unassignable(self, env):
        pytest.raises(TemplateSyntaxError, env.from_string,
                      '{% for forloop in seq %}...{% endfor %}')

    def test_scoped_special_var(self, env):
        t = env.from_string(
            '{% for s in seq %}[{{ forloop.first }}{% for c in s %}'
            '|{{ forloop.first }}{% endfor %}]{% endfor %}')
        assert t.render(seq=('ab', 'cd')) \
            == '[True|True|False][False|True|False]'

    def test_scoped_loop_var(self, env):
        t = env.from_string('{% for x in seq %}{{ forloop.first }}'
                            '{% for y in seq %}{% endfor %}{% endfor %}')
        assert t.render(seq='ab') == 'TrueFalse'
        t = env.from_string('{% for x in seq %}{% for y in seq %}'
                            '{{ forloop.first }}{% endfor %}{% endfor %}')
        assert t.render(seq='ab') == 'TrueFalseTrueFalse'

    def test_recursive_empty_loop_iter(self, env):
        t = env.from_string('''
        {%- for item in foo recursive -%}{%- endfor -%}
        ''')
        assert t.render(dict(foo=[])) == ''

    def test_call_in_loop(self, env):
        t = env.from_string('''
        {%- macro do_something() -%}
            [{{ caller() }}]
        {%- endmacro %}

        {%- for i in [1, 2, 3] %}
            {%- call do_something() -%}
                {{ i }}
            {%- endcall %}
        {%- endfor -%}
        ''')
        assert t.render() == '[1][2][3]'

    def test_scoping_bug(self, env):
        t = env.from_string('''
        {%- for item in foo %}...{{ item }}...{% endfor %}
        {%- macro item(a) %}...{{ a }}...{% endmacro %}
        {{- item(2) -}}
        ''')
        assert t.render(foo=(1,)) == '...1......2...'

    def test_unpacking(self, env):
        tmpl = env.from_string('{% for a, b, c in [[1, 2, 3]] %}'
                               '{{ a }}|{{ b }}|{{ c }}{% endfor %}')
        assert tmpl.render() == '1|2|3'


@pytest.mark.core_tags
@pytest.mark.if_condition
class TestIfCondition():

    def test_simple(self, env):
        tmpl = env.from_string('''{% if true %}...{% endif %}''')
        assert tmpl.render() == '...'

    def test_elsif(self, env):
        tmpl = env.from_string('''{% if false %}XXX{% elsif true
            %}...{% else %}XXX{% endif %}''')
        assert tmpl.render() == '...'

    def test_else(self, env):
        tmpl = env.from_string('{% if false %}XXX{% else %}...{% endif %}')
        assert tmpl.render() == '...'

    def test_empty(self, env):
        tmpl = env.from_string('[{% if true %}{% else %}{% endif %}]')
        assert tmpl.render() == '[]'

    def test_complete(self, env):
        tmpl = env.from_string('{% if a %}A{% elsif b %}B{% elsif c == d %}'
                               'C{% else %}D{% endif %}')
        assert tmpl.render(a=None, b=False, c=42, d=42.0) == 'C'

    def test_no_scope(self, env):
        tmpl = env.from_string(
            '{% if a %}{% set foo = 1 %}{% endif %}{{ foo }}')
        assert tmpl.render(a=True) == '1'
        tmpl = env.from_string(
            '{% if true %}{% set foo = 1 %}{% endif %}{{ foo }}')
        assert tmpl.render() == '1'

    def test_zero(self, env):
        tmpl = env.from_string('''{% if 0 %}...{% endif %}''')
        assert tmpl.render() == '...'

    def test_emptystring(self, env):
        tmpl = env.from_string('''{% if "" %}...{% endif %}''')
        assert tmpl.render() == '...'

    def test_emptylist(self, env):
        tmpl = env.from_string('''{% if [] %}...{% endif %}''')
        assert tmpl.render() == '...'

    def test_emptydict(self, env):
        tmpl = env.from_string('''{% if {} %}...{% endif %}''')
        assert tmpl.render() == '...'


@pytest.mark.core_tags
@pytest.mark.unless_condition
class TestUnlessCondition():
    def test_simple(self, env):
        tmpl = env.from_string('''{% unless false %}...{% endunless %}''')
        assert tmpl.render() == '...'

    def test_elsif(self, env):
        tmpl = env.from_string('''{% unless true %}XXX{% elsif true
            %}...{% else %}XXX{% endunless %}''')
        assert tmpl.render() == '...'

    def test_else(self, env):
        tmpl = env.from_string('{% unless true %}XXX{% else %}...{% endunless %}')
        assert tmpl.render() == '...'

    def test_empty(self, env):
        tmpl = env.from_string('[{% unless false %}{% else %}{% endunless %}]')
        assert tmpl.render() == '[]'

    def test_complete(self, env):
        tmpl = env.from_string('{% unless not a %}A{% elsif b %}B{% elsif c == d %}'
                               'C{% else %}D{% endunless %}')
        assert tmpl.render(a=0, b=False, c=42, d=42.0) == 'C'

    def test_no_scope(self, env):
        tmpl = env.from_string(
            '{% unless not a %}{% set foo = 1 %}{% endunless %}{{ foo }}')
        assert tmpl.render(a=True) == '1'
        tmpl = env.from_string(
            '{% unless false %}{% set foo = 1 %}{% endunless %}{{ foo }}')
        assert tmpl.render() == '1'


@pytest.mark.core_tags
@pytest.mark.macros
class TestMacros():
    def test_simple(self, env_trim):
        tmpl = env_trim.from_string('''\
{% macro say_hello(name) %}Hello {{ name }}!{% endmacro %}
{{ say_hello('Peter') }}''')
        assert tmpl.render() == 'Hello Peter!'

    def test_scoping(self, env_trim):
        tmpl = env_trim.from_string('''\
{% macro level1(data1) %}
{% macro level2(data2) %}{{ data1 }}|{{ data2 }}{% endmacro %}
{{ level2('bar') }}{% endmacro %}
{{ level1('foo') }}''')
        assert tmpl.render() == 'foo|bar'

    def test_arguments(self, env_trim):
        tmpl = env_trim.from_string('''\
{% macro m(a, b, c='c', d='d') %}{{ a }}|{{ b }}|{{ c }}|{{ d }}{% endmacro %}
{{ m() }}|{{ m('a') }}|{{ m('a', 'b') }}|{{ m(1, 2, 3) }}''')
        assert tmpl.render() == '||c|d|a||c|d|a|b|c|d|1|2|3|d'

    def test_arguments_defaults_nonsense(self, env_trim):
        pytest.raises(TemplateSyntaxError, env_trim.from_string, '''\
{% macro m(a, b=1, c) %}a={{ a }}, b={{ b }}, c={{ c }}{% endmacro %}''')

    def test_caller_defaults_nonsense(self, env_trim):
        pytest.raises(TemplateSyntaxError, env_trim.from_string, '''\
{% macro a() %}{{ caller() }}{% endmacro %}
{% call(x, y=1, z) a() %}{% endcall %}''')

    def test_varargs(self, env_trim):
        tmpl = env_trim.from_string('''\
{% macro test() %}{{ varargs|join('|') }}{% endmacro %}\
{{ test(1, 2, 3) }}''')
        assert tmpl.render() == '1|2|3'

    def test_simple_call(self, env_trim):
        tmpl = env_trim.from_string('''\
{% macro test() %}[[{{ caller() }}]]{% endmacro %}\
{% call test() %}data{% endcall %}''')
        assert tmpl.render() == '[[data]]'

    def test_complex_call(self, env_trim):
        tmpl = env_trim.from_string('''\
{% macro test() %}[[{{ caller('data') }}]]{% endmacro %}\
{% call(data) test() %}{{ data }}{% endcall %}''')
        assert tmpl.render() == '[[data]]'

    def test_caller_undefined(self, env_trim):
        tmpl = env_trim.from_string('''\
{% set caller = 42 %}\
{% macro test() %}{{ caller is not defined }}{% endmacro %}\
{{ test() }}''')
        assert tmpl.render() == 'True'

    def test_include(self, env_trim):
        env_trim = Environment(
            loader=DictLoader({
                'include': '{% macro test(foo) %}[{{ foo }}]{% endmacro %}'
            })
        )
        tmpl = env_trim.from_string(
            '{% from "include" import test %}{{ test("foo") }}')
        assert tmpl.render() == '[foo]'

    def test_macro_api(self, env_trim):
        tmpl = env_trim.from_string(
            '{% macro foo(a, b) %}{% endmacro %}'
            '{% macro bar() %}{{ varargs }}{{ kwargs }}{% endmacro %}'
            '{% macro baz() %}{{ caller() }}{% endmacro %}')
        assert tmpl.module.foo.arguments == ('a', 'b')
        assert tmpl.module.foo.defaults == ()
        assert tmpl.module.foo.name == 'foo'
        assert not tmpl.module.foo.caller
        assert not tmpl.module.foo.catch_kwargs
        assert not tmpl.module.foo.catch_varargs
        assert tmpl.module.bar.arguments == ()
        assert tmpl.module.bar.defaults == ()
        assert not tmpl.module.bar.caller
        assert tmpl.module.bar.catch_kwargs
        assert tmpl.module.bar.catch_varargs
        assert tmpl.module.baz.caller

    def test_callself(self, env_trim):
        tmpl = env_trim.from_string('{% macro foo(x) %}{{ x }}{% if x > 1 %}|'
                                    '{{ foo(x - 1) }}{% endif %}{% endmacro %}'
                                    '{{ foo(5) }}')
        assert tmpl.render() == '5|4|3|2|1'


@pytest.mark.core_tags
@pytest.mark.set
class TestSet():
    def test_normal(self, env_trim):
        tmpl = env_trim.from_string('{% set foo = 1 %}{{ foo }}')
        assert tmpl.render() == '1'
        assert tmpl.module.foo == 1

    def test_block(self, env_trim):
        tmpl = env_trim.from_string('{% set foo %}42{% endset %}{{ foo }}')
        assert tmpl.render() == '42'
        assert tmpl.module.foo == u'42'


@pytest.mark.core_tags
@pytest.mark.assign
class TestAssign():
    def test_normal(self, env_trim):
        tmpl = env_trim.from_string('{% assign foo = 1 %}{{ foo }}')
        assert tmpl.render() == '1'
        assert tmpl.module.foo == 1

    def test_block(self, env_trim):
        tmpl = env_trim.from_string('{% assign foo %}42{% endassign %}{{ foo }}')
        assert tmpl.render() == '42'
        assert tmpl.module.foo == u'42'


@pytest.mark.core_tags
@pytest.mark.capture
class TestCapture():
    def test_normal(self, env_trim):
        tmpl = env_trim.from_string('{% capture foo = 1 %}{{ foo }}')
        assert tmpl.render() == '1'
        assert tmpl.module.foo == 1

    def test_block(self, env_trim):
        tmpl = env_trim.from_string('{% capture foo %}42{% endcapture %}{{ foo }}')
        assert tmpl.render() == '42'
        assert tmpl.module.foo == u'42'
