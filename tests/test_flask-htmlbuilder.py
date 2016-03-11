# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from nose.tools import raises

from flask import Flask, g, Markup

from flaskext.htmlbuilder import html, render, render_template, root_block
from flaskext.htmlbuilder import block, Block, RootBlock, Context, init_htmlbuilder, Attr


def rn(element):
    return render(element, None)


def test_single_attribute():
    assert rn(html.a(name='value')) == '<a name="value" />'


def test_multiple_attribute():
    result = rn(html.a(first='one', second='two'))
    assert result in ['<a first="one" second="two" />', '<a second="two" first="one" />']


def test_unicode_attribute_values():
    assert rn(html.a(chars=u'\u03a0\u03a3\u03a9')) == u'<a chars="\u03a0\u03a3\u03a9" />'


def test_none_attribute_values():
    assert rn(html.a(id=None)) == u'<a />'
    assert rn(html.a(a=None, b='b', c=None)) == u'<a b="b" />'


def test_attribute_value_escaping():
    assert rn(html.a(chars='<"&>')) == '<a chars="&lt;&quot;&amp;&gt;" />'


def test_colon_unmangling():
    assert rn(html.a(first__second='value')) == '<a first:second="value" />'


def test_python_keyword_unmangling():
    assert rn(html.a(class_='value')) == '<a class="value" />'
    assert rn(html.a(else_='value')) == '<a else="value" />'
    assert rn(html.a(id_='value')) == '<a id-="value" />'

    assert rn(html.del_('Text')) == '<del>Text</del>'


def test_void_elements():
    assert rn(html.a(name='value')) == '<a name="value" />'
    assert rn(html.a) == '<a />'


def test_empty_children():
    assert rn(html.a(name='value')()) == '<a name="value"></a>'
    assert rn(html.a()) == '<a></a>'


def test_one_text_child():
    assert rn(html.a(name='value')('Text')) == '<a name="value">Text</a>'
    assert rn(html.a('Text')) == '<a>Text</a>'


def test_many_children():
    assert rn(html.a(name='value')(html.b(first='one'), 'Text', html.c())) == '<a name="value"><b first="one" />Text<c></c></a>'


def test_nesting():
    assert rn(html.a(name='value')(html.b('Text'), html.c(html.d, html.e()))) == '<a name="value"><b>Text</b><c><d /><e></e></c></a>'


def test_single_element_indenting():
    assert render(html.a) == '<a />\n'
    assert render(html.a()) == '<a></a>\n'
    assert render(html.a(name='value')) == '<a name="value" />\n'
    assert render(html.a(name='value')()) == '<a name="value"></a>\n'


def test_one_text_child_indenting():
    assert render(html.a(name='value')('Text')) == '<a name="value">Text</a>\n'
    assert render(html.a('Text')) == '<a>Text</a>\n'


def test_one_non_text_child_indenting():
    assert render(html.a(html.b)) == '<a>\n  <b />\n</a>\n'


def test_many_text_child_indenting():
    assert render(html.a('One', 'Two')) == '<a>\n  One\n  Two\n</a>\n'


def test_many_child_indenting():
    assert render(html.a(name='value')(html.b(first='one'), 'Text', html.c())) == '<a name="value">\n  <b first="one" />\n  Text\n  <c></c>\n</a>\n'


def test_nested_indentating():
    elements = [
        html.doctype('html'),
        html.html(lang='en', class_='no-js')(
            html.head(
                html.title('Hello')
            ),
            html.body(
                html.comment(' Body starts here '),
                html.p('Hello World!')
            )
        )
    ]

    assert render(elements) == """<!doctype html>
<html lang="en" class="no-js">
  <head>
    <title>Hello</title>
  </head>
  <body>
    <!-- Body starts here -->
    <p>Hello World!</p>
  </body>
</html>
"""


def test_unicode_text():
    assert rn(html.a(u'\u03a0\u03a3\u03a9')) == u'<a>\u03a0\u03a3\u03a9</a>'


def test_text_escaping():
    assert rn(html.a('aaa<aaa"aaa&nbsp;aaa>')) == '<a>aaa&lt;aaa"aaa&amp;nbsp;aaa&gt;</a>'


def test_raw_text_render():
    assert rn('One Two') == 'One Two'
    assert rn(u'\u03a0\u03a3\u03a9') == u'\u03a0\u03a3\u03a9'
    assert rn('aaa<aaa"aaa&nbsp;aaa>') == 'aaa&lt;aaa"aaa&amp;nbsp;aaa&gt;'


def test_iteratable_render():
    assert rn([html.a, 'Text', html.b()]) == '<a />Text<b></b>'
    assert rn(html.c([html.a, 'Text', html.b()])) == '<c><a />Text<b></b></c>'


def test_nested_iteratable_render():
    assert rn([html.a, ['Text', html.b()]]) == '<a />Text<b></b>'


def test_join():
    assert render(html.p(html.join(html.a, 'Text', html.b()))) == '<p>\n  <a />Text<b></b>\n</p>\n'
    assert render(html.join(html.p(html.a, 'Text', html.b()))) == '<p><a />Text<b></b></p>\n'
    assert rn(html.join(html.p(html.a, 'Text', html.b()))) == '<p><a />Text<b></b></p>'


def test_comment():
    assert rn(html.comment('Comment')) == '<!--Comment-->'
    assert render(html.p(html.comment('Comment'))) == '<p>\n  <!--Comment-->\n</p>\n'


def test_doctype():
    assert rn(html.doctype('html')) == '<!doctype html>'
    assert render(html.doctype('html')) == '<!doctype html>\n'


def test_safe():
    assert rn(html.safe('<strong>&nbsp;Text&nbsp;</strong>')) == '<strong>&nbsp;Text&nbsp;</strong>'
    assert rn(html.p(html.safe('<strong>&nbsp;Text&nbsp;</strong>'))) == '<p><strong>&nbsp;Text&nbsp;</strong></p>'
    assert render(html.p(html.safe('<strong>&nbsp;Text&nbsp;</strong>'))) == '<p>\n  <strong>&nbsp;Text&nbsp;</strong>\n</p>\n'


def test_newline():
    assert render([html.p('First'), html.newline(), html.p('Second')]) == '<p>First</p>\n\n<p>Second</p>\n'
    assert render(html.div(html.p('First'), html.newline(), html.p('Second'))) == \
           '<div>\n  <p>First</p>\n  \n  <p>Second</p>\n</div>\n'
    assert rn([html.p('First'), html.newline(), html.p('Second')]) == '<p>First</p><p>Second</p>'


def test_render_level():
    assert render(html.p(html.a('Text')), level=1) == '  <p>\n    <a>Text</a>\n  </p>\n'
    assert render(html.p(html.a('Text')), level=2) == '    <p>\n      <a>Text</a>\n    </p>\n'


@raises(AttributeError)
def test_escape_attribute_numbers():
    render(html.a(x=5))


@raises(TypeError)
def test_escape_numbers():
    render(html.a(5))


def test_root_block_decorator():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/')
    def return_root():
        g.blocks['body'] = 'Hello, World!'
        return render_template()

    @root_block()
    def site_root():
        return [html.doctype('html'), html.html(html.head(), html.body(g.blocks['body']))]

    client = app.test_client()
    result = client.get('/')
    assert result.mimetype == 'text/html'
    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>Hello, World!</body>
</html>
"""


def test_block_decorator():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/')
    def return_root():
        return render_template()

    @root_block()
    def site_root():
        return [html.doctype('html'), html.html(html.head(), html.body(g.blocks['body']))]

    @block('body', site_root)
    def site_body():
        return html.p('Hello, World!')

    client = app.test_client()
    result = client.get('/')
    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <p>Hello, World!</p>
  </body>
</html>
"""

def test_multiple_views():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        return render_template()

    @app.route('/b')
    def view_b():
        return render_template()

    @root_block()
    def site_root():
        return [html.doctype('html'), html.html(html.head(), html.body(g.blocks['body']))]

    @block('body', site_root, view_a)
    def view_a_body():
        return html.p('Hello, View A!')

    @block('body', site_root, view_b)
    def view_b_body():
        return html.p('Hello, View B!')

    client = app.test_client()

    result = client.get('/a')
    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <p>Hello, View A!</p>
  </body>
</html>
"""
    result = client.get('/b')
    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <p>Hello, View B!</p>
  </body>
</html>
"""

def test_default_block():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        return render_template()

    @app.route('/b')
    def view_b():
        return render_template()

    @root_block()
    def site_root():
        return [html.doctype('html'), html.html(html.head(), html.body(g.blocks['body']))]

    @block('body', site_root, view_a)
    def view_a_body():
        return html.p('Hello, View A!')

    @block('body', site_root)
    def default_body():
        return html.p('Hello, Default Block!')

    client = app.test_client()

    result = client.get('/a')
    assert result.data == """<!doctype html>
<html>
  <head></head>
  <body>
    <p>Hello, View A!</p>
  </body>
</html>
"""
    result = client.get('/b')
    assert result.data == """<!doctype html>
<html>
  <head></head>
  <body>
    <p>Hello, Default Block!</p>
  </body>
</html>
"""

def test_multiple_contexts():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        return render_template()

    @root_block()
    def site_root():
        return [
            html.doctype('html'),
            html.html(
                html.head(
                    html.title(
                        g.blocks['title']
                    )
                ),
                html.body(
                    g.blocks['body']
                )
            )
        ]

    @block('body', site_root)
    def site_body():
        return html.p('This is the body.')

    @block('title', site_root)
    def site_title():
        return 'Title'

    client = app.test_client()
    result = client.get('/a')

    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head>
    <title>Title</title>
  </head>
  <body>
    <p>This is the body.</p>
  </body>
</html>
"""

def test_deep_inheritance():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        return render_template()

    @root_block()
    def site_root():
        return [
            html.doctype('html'),
            html.html(
                html.head(),
                html.body(
                    g.blocks['body']
                )
            )
        ]

    @block('body', site_root)
    def site_body():
        return html.div(class_='container')(g.blocks['container'])

    @block('container', site_body)
    def container_body():
        return html.div('Container content.')

    client = app.test_client()
    result = client.get('/a')

    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <div class="container">
      <div>Container content.</div>
    </div>
  </body>
</html>
"""


def test_alternative_definition():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        return render_template()

    @app.route('/b')
    def view_b():
        return render_template()

    def site_root():
        return [
            html.doctype('html'),
            html.html(
                html.head(),
                html.body(
                    g.blocks['body']
                )
            )
        ]

    def default_body():
        return html.p('Default body.')

    def view_a_body():
        return html.div(class_='container')(g.blocks['container'])

    def view_a_container():
        return html.div('Container content.')

    RootBlock(site_root)(
        Context('body')(
            Block(default_body),
            Block(view_a_body, view_a)(
                Context('container')(
                    Block(view_a_container)
                )
            )
        )
    )

    client = app.test_client()

    result = client.get('/a')
    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <div class="container">
      <div>Container content.</div>
    </div>
  </body>
</html>
"""

    result = client.get('/b')
    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <p>Default body.</p>
  </body>
</html>
"""

def test_markup():
    assert Markup(html.a(name='value')(html.b(first='one'), 'Text', html.c())) == '<a name="value"><b first="one" />Text<c></c></a>'
    assert Markup(html.p(html.comment('Comment'))) == '<p><!--Comment--></p>'
    assert Markup(html.p(html.safe('<strong>&nbsp;Text&nbsp;</strong>'))) == '<p><strong>&nbsp;Text&nbsp;</strong></p>'
    assert Markup(html.safe('<strong>&nbsp;Text&nbsp;</strong>')) == '<strong>&nbsp;Text&nbsp;</strong>'

    assert rn(html.p(Markup('<strong>&nbsp;Text&nbsp;</strong>'))) == '<p><strong>&nbsp;Text&nbsp;</strong></p>'
    assert rn(html.p(Markup('&nbsp; '), Markup('<strong>One</strong>'))) == '<p>&nbsp; <strong>One</strong></p>'
    assert render(html.p(Markup('&nbsp; '), Markup('<strong>One</strong>'))) == u'<p>\n  &nbsp; \n  <strong>One</strong>\n</p>\n'


def test_html_block_has_block():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        html.block('container')(
            html.div('Container content.')
        )
        return render_template()

    @root_block()
    def site_root():
        return [
            html.doctype('html'),
            html.html(
                html.head(),
                html.body(
                    g.blocks['body']
                )
            )
        ]

    @block('body', site_root)
    def site_body():
        return html.has_block('container')(
            html.div(class_='container')(
                html.block('container'),
                html.block('undefined'),
                html.has_block('noblock')(
                    html.p()
                )
            )
        )

    client = app.test_client()
    result = client.get('/a')

    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head></head>
  <body>
    <div class="container">
      <div>Container content.</div>
    </div>
  </body>
</html>
"""


def test_attr_has_attr():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        g.attrs['description'] = 'A description'
        return render_template()

    @root_block()
    def site_root():
        return [
            html.doctype('html'),
            html.html(
                html.head(
                    html.has_attr('description')(
                        html.meta(content=Attr('description'))
                    ),
                    html.has_attr('author')(
                        html.meta(content=Attr('author'))
                    )
                ),
                html.body()
            )
        ]

    client = app.test_client()
    result = client.get('/a')

    assert result.data.decode('utf-8') == """<!doctype html>
<html>
  <head>
    <meta content="A description" />
  </head>
  <body></body>
</html>
"""

def test_default_block():
    app = Flask(__name__)
    init_htmlbuilder(app)

    @app.route('/a')
    def view_a():
        return render_template()

    @app.route('/b')
    def view_b():
        html.block('title')('New Title')
        return render_template()

    @root_block()
    def site_root():
        return html.title(
            html.block('title')(
                'Default Title'
            )
        )

    client = app.test_client()
    result = client.get('/a')
    assert result.data.decode('utf-8') == """<title>
  Default Title
</title>
"""

    result = client.get('/b')
    assert result.data.decode('utf-8') == """<title>
  New Title
</title>
"""

    result = client.get('/a')
    assert result.data.decode('utf-8') == """<title>
  Default Title
</title>
"""
