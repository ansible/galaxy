# (c) 2012-2018, Ansible by Red Hat
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


# TODO(cutwater): Pass context variable as parameter
class ContentBlockNode(template.Node):
    def __init__(self, block_name):
        self.blockname = block_name

    def render(self, context):
        # FIXME(cutwater): THIS IS UNSAFE
        # Injects content from database as is. Additional sanitizing required.
        # Consider using `bleach` python library for that purpose.
        try:
            return context['contentblocks'][self.blockname].content
        except KeyError:
            block = models.ContentBlock.objects.get(name=self.blockname)
            return block.content


@register.tag('contentblock')
def contentblock_tag(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "'{0}' takes one argument (name)".format(bits[0]))
    block_name = bits[1]
    return ContentBlockNode(block_name)
