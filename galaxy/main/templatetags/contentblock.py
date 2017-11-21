# (c) 2012-2017, Ansible by Red Hat
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

from django import template

from galaxy.main import models

register = template.Library()


# TODO(cutwater): Simplify contentblocks, remove image and title
# Render as a simple tag, not a block tag
class ContentBlockNode(template.Node):
    def __init__(self, nodelist, block_name):
        self.nodelist = nodelist
        self.blockname = block_name

    def render(self, context):
        # TODO(cutwater): Pre-load content blocks for view
        block = models.ContentBlock.objects.get(name=self.blockname)
        context['contentblock'] = block
        return self.nodelist.render(context)


@register.tag('contentblock')
def contentblock_tag(parser, token):
    bits = token.split_contents()

    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "'{0}' takes one argument (name)".format(bits[0]))
    block_name = bits[1]

    nodelist = parser.parse(('endcontentblock', ))
    parser.delete_first_token()
    return ContentBlockNode(nodelist, block_name)
