# -*- coding: utf-8 -*-
"""
Liquid
~~~~~~

Liquid is a template engine written in pure Python.  It provides a
`Django`_ inspired non-XML syntax but supports inline expressions and
an optional `sandboxed`_ environment.

Nutshell
--------

Here a small example of a Liquid template::

    {% extends 'base.html' %}
    {% block title %}Memberlist{% endblock %}
    {% block content %}
      <ul>
      {% for user in users %}
        <li><a href="{{ user.url }}">{{ user.username }}</a></li>
      {% endfor %}
      </ul>
    {% endblock %}

Philosophy
----------

Application logic is for the controller but don't try to make the life
for the template designer too hard by giving him too few functionality.

.. _sandboxed: http://en.wikipedia.org/wiki/Sandbox_(computer_security)
.. _Django: http://www.djangoproject.com/
.. _Jinja2 webpage: http://jinja.pocoo.org/
.. _Liquid by Shopify: http://shopify.github.io/liquid/
"""
from setuptools import setup


setup(
    name='Liquid',
    version='0.2.9.dev',
    url='http://www.sumsum.se/',
    license='BSD',
    author='Mikko Hellsing',
    author_email='mikkohellsing@gmail.com',
    description='A small but fast and easy to use stand-alone template '
                'engine written in pure python.',
    long_description=__doc__,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    packages=['jinja2'],
    install_requires=['MarkupSafe'],
    extras_require={'i18n': ['Babel>=0.8']},
    include_package_data=True,
    entry_points="""
    [babel.extractors]
    liquid = liquid.ext:babel_extract[i18n]
    """
)
