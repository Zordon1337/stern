
from app.common.constants import regexes
from .parser import Parser
import config

parser = Parser()
parser.add_simple_formatter('b', '<b>%(value)s</b>')
parser.add_simple_formatter('i', '<i>%(value)s</i>')
parser.add_simple_formatter('u', '<u>%(value)s</u>')
parser.add_simple_formatter('heading', '<h2>%(value)s</h2>')
parser.add_simple_formatter('strike', '<strike>%(value)s</strike>')
parser.add_simple_formatter('centre', '<center>%(value)s</center>')
parser.add_simple_formatter('c', '<div class="code-block">%(value)s</div>')

parser.add_simple_formatter(
    'img',
    '<img src="%(value)s" alt="" loading="lazy">',
    replace_links=False
)

parser.add_simple_formatter(
    'code',
    '%(value)s',
    same_tag_closes=True,
    render_embedded=False,
    transform_newlines=False,
    escape_html=False,
    replace_links=False
)

parser.add_simple_formatter(
    '*',
    '<li>%(value)s</li>',
    same_tag_closes=True
)

# TODO: Add css & js for this
parser.add_simple_formatter(
    'spoilerbox',
    '<div class="spoiler">'
    '<div class="spoiler-head" onclick="return toggleSpoiler(this);">SPOILER</div>'
    '<div class="spoiler-body">%(value)s</div>'
    '</div>'
)

@parser.formatter('box')
def render_box(tag_name, value, options, parent, context):
    return '<div class="spoiler">' \
           '<div class="spoiler-head" onclick="return toggleSpoiler(this);">%s</div>' \
           '<div class="spoiler-body">%s</div>' \
           '</div>' % (options.get('box', ''), value)

@parser.formatter('color')
def render_color(tag_name, value, options, parent, context):
    return '<span style="color:%s;">%s</span>' % (options.get('color', ''), value)

@parser.formatter('profile')
def render_profile(tag_name, value, options, parent, context):
    return '<a href="https://osu.%s/u/%s">%s</a>' % (config.DOMAIN_NAME, options.get('profile', value), value)

@parser.formatter('url')
def render_link(tag_name, value, options, parent, context):
    return '<a href="%s">%s</a>' % (options.get('url', ''), value)

@parser.formatter('quote')
def render_code(tag_name, value, options, parent, context):
    if 'quote' not in options:
        return '<blockquote>%s</blockquote>' % value

    return '<blockquote>' \
           '<h4>%s wrote:</h4>' \
           '%s' \
           '</blockquote>' % (options["quote"], value)

@parser.formatter('size')
def render_size(tag_name, value, options, parent, context):
    if 'size' not in options:
        size = '100'

    if (size := options['size']).isdigit():
        return '<span style="font-size:%s%%;">%s</span>' % (size, value)

    size_strings = {
        'tiny': 50,
        'small': 85,
        'normal': 100,
        'large': 150
    }

    if size not in size_strings:
        return value

    return '<span style="font-size:%s;">%s</span>' % (size_strings[size], value)

@parser.formatter('list')
def render_list(tag_name, value, options, parent, context):
    if 'list' in options:
        return '<ol>%s</ol>' % value

    return '<ul>%s</ul>' % value

@parser.formatter('email')
def render_email(tag_name, value, options, parent, context):
    email = options.get('email') \
        if 'email' in options \
        else value

    if not (regexes.EMAIL.match(email)):
        return value

    return '<a href="mailto:%s">%s</a>' % (email, value)
