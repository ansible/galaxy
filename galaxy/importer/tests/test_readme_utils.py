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

from django.test import TestCase

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


class ReadmeRenderHtmlTestCase(TestCase):
    def setUp(self):
        self.Data = collections.namedtuple('Data', 'text mimetype')

    def call_render(self, raw_text, mimetype):
        readme_file = self.Data(text=raw_text, mimetype=mimetype)
        return utils.readme.render_html(readme_file)

    def test_render_simple(self):
        html = self.call_render(TEXT_SIMPLE, 'text/x-rst')
        self.assertEqual(html, '')

        html = self.call_render(TEXT_SIMPLE, 'text/markdown')
        self.assertEqual(html, '<p>{}</p>'.format(TEXT_SIMPLE))

    def test_render_bad_tag(self):
        html = self.call_render(TEXT_BAD_TAG, 'text/x-rst')
        self.assertEqual(html, '')
        self.assertNotIn('<script>', html)

        html = self.call_render(TEXT_BAD_TAG, 'text/markdown')
        self.assertNotIn('<script>', html)

    def test_render_bad_html_hidden_in_md(self):
        html = self.call_render(TEXT_BAD_HTML_IN_MD, 'text/x-rst')
        self.assertEqual(html, '')
        self.assertNotIn('javascript', html)

        html = self.call_render(TEXT_BAD_HTML_IN_MD, 'text/markdown')
        self.assertNotIn('javascript', html)

    def test_render_formatting(self):
        html = self.call_render(TEXT_FORMATTING, 'text/x-rst')
        self.assertEqual(html, '')

        html = self.call_render(TEXT_FORMATTING, 'text/markdown')
        self.assertIn('<h1>Role</h1>', html)
        self.assertIn('<a href="https://www.example.com">Tool</a>', html)
        self.assertIn('<code>$PATH</code>', html)
        self.assertIn('<h3>Installation</h3>', html)
        self.assertIn('<code>package_version: "1.2.0"', html)
        self.assertIn('<blockquote>\n<p>NOTE:', html)
        self.assertIn('Tool \'feature\' is <em>beta</em>', html)
        self.assertIn('<ul>\n<li>Item1</li>', html)
