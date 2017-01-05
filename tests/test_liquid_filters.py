import pytest
from jinja2 import Markup, Environment
from jinja2._compat import text_type, implements_to_string


@pytest.mark.liquid_filter
class TestLiquidFilter():

    def test_abs(self, env):
        """
        Test taken from: https://github.com/Shopify/liquid/blob/b2feeacbce8e4a718bde9bc9fa9d00e44ab32351/test/integration/standard_filter_test.rb#L407
        """
        tmpl = env.from_string('{{ 17 | abs }}')
        assert tmpl.render() == '17'
        tmpl = env.from_string('{{ -17 | abs }}')
        assert tmpl.render() == '17'
        tmpl = env.from_string("{{ '17' | abs }}")
        assert tmpl.render() == '17'
        tmpl = env.from_string("{{ '-17' | abs }}")
        assert tmpl.render() == '17'
        tmpl = env.from_string("{{ 0 | abs }}")
        assert tmpl.render() == '0'
        tmpl = env.from_string("{{ '0' | abs }}")
        assert tmpl.render() == '0'
        tmpl = env.from_string("{{ 17.42 | abs }}")
        assert tmpl.render() == '17.42'
        tmpl = env.from_string("{{ -17.42 | abs }}")
        assert tmpl.render() == '17.42'
        tmpl = env.from_string("{{ '17.42' | abs }}")
        assert tmpl.render() == '17.42'
        tmpl = env.from_string("{{ '-17.42' | abs }}")
        assert tmpl.render() == '17.42'

    def test_append(self, env):
        """
        Test taken from: https://github.com/Shopify/liquid/blob/b2feeacbce8e4a718bde9bc9fa9d00e44ab32351/test/integration/standard_filter_test.rb#L486
        """
        ctx = {'a': 'bc', 'b': 'd'}
        tmpl = env.from_string("{{ a | append: 'd'}}")
        assert tmpl.render(**ctx) == 'bcd'
        tmpl = env.from_string("{{ a | append: b}}")
        assert tmpl.render(**ctx) == 'bcd'

    def test_capitalize(self, env):
        """
        Test taken from: https://github.com/Shopify/liquid/blob/64fca66ef5dfd7cf1acef0a7b8cdd825756eb681/test/integration/filter_test.rb#L128
        """
        tmpl = env.from_string("{{ var | capitalize }}")
        assert tmpl.render(var='blub') == 'Blub'

    def test_ceil(self, env):
        """
        Test taken from: https://github.com/Shopify/liquid/blob/b2feeacbce8e4a718bde9bc9fa9d00e44ab32351/test/integration/standard_filter_test.rb#L466
        """
        tmpl = env.from_string("{{ input | ceil }}")
        assert tmpl.render(input=4.6) == '5'
        tmpl = env.from_string("{{ 4.3 | ceil }}")
        assert tmpl.render() == '5'
        tmpl = env.from_string("{{ 1.0 | divided_by: 0.0 | ceil }}")
        pytest.raises(ZeroDivisionError)
        tmpl = env.from_string("{{ price | ceil }}")
        assert tmpl.render(price='4.6') == '5'

    def test_divided_by(self, env):
        """
        Test taken from: https://github.com/Shopify/liquid/blob/b2feeacbce8e4a718bde9bc9fa9d00e44ab32351/test/integration/standard_filter_test.rb#L430
        """
        tmpl = env.from_string("{{ 12 | divided_by:3 }}")
        assert tmpl.render() == '4'
        tmpl = env.from_string("{{ 14 | divided_by:3 }}")
        assert tmpl.render() == '4'
        tmpl = env.from_string("{{ 15 | divided_by:3 }}")
        assert tmpl.render() == '5'
        tmpl = env.from_string("{{ 5 | divided_by:0 }}")
        pytest.raises(ZeroDivisionError)
        tmpl = env.from_string("{{ 2.0 | divided_by:4 }}")
        assert tmpl.render() == '0.5'
        tmpl = env.from_string("{{ 1 | modulo: 0 }}")
        pytest.raises(ZeroDivisionError)
        tmpl = env.from_string("{{ price | divided_by:2 }}")
        assert tmpl.render(price='10') == '5'
