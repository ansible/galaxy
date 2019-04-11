# (c) 2012-2019, Ansible by Red Hat
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by
# the Apache Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Apache License for more details.
#
# You should have received a copy of the Apache License
# along with Galaxy.  If not, see <http://www.apache.org/licenses/>.

import collections

from galaxy.importer import utils

TEXT_SIMPLE = 'A simple description'
TEXT_BAD_TAG = 'hello <script>cruel</script> world'
TEXT_BAD_HTML_IN_MD = '''
> hello <a name="n"
> href="javascript:something_bad()">*you*</a>
'''
TEXT_FORMATTING = '''
# Role

[Tool](https://www.example.com) installed in `$PATH`

### Installation

    package_version: "1.2.0"

> NOTE: Tool 'feature' is _beta_

* Item1
* Item2
'''

Data = collections.namedtuple('Data', 'text mimetype')


def call_render(raw_text, mimetype):
    readme_file = Data(text=raw_text, mimetype=mimetype)
    return utils.readme.render_html(readme_file)


def test_render_simple():
    html = call_render(TEXT_SIMPLE, 'text/x-rst')
    assert html == ''

    html = call_render(TEXT_SIMPLE, 'text/markdown')
    assert html == '<p>{}</p>'.format(TEXT_SIMPLE)


def test_render_bad_tag():
    html = call_render(TEXT_BAD_TAG, 'text/x-rst')
    assert html == ''
    assert '<script>' not in html

    html = call_render(TEXT_BAD_TAG, 'text/markdown')
    assert '<script>' not in html


def test_render_bad_html_hidden_in_md():
    html = call_render(TEXT_BAD_HTML_IN_MD, 'text/x-rst')
    assert html == ''
    assert 'javascript' not in html

    html = call_render(TEXT_BAD_HTML_IN_MD, 'text/markdown')
    assert 'javascript' not in html


def test_render_formatting():
    html = call_render(TEXT_FORMATTING, 'text/x-rst')
    assert html == ''

    html = call_render(TEXT_FORMATTING, 'text/markdown')
    assert '<h1>Role</h1>' in html
    assert '<a href="https://www.example.com">Tool</a>' in html
    assert '<code>$PATH</code>' in html
    assert '<h3>Installation</h3>' in html
    assert '<code>package_version: "1.2.0"' in html
    assert '<blockquote>\n<p>NOTE:' in html
    assert 'Tool \'feature\' is <em>beta</em>' in html
    assert '<ul>\n<li>Item1</li>' in html
