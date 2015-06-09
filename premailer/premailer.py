import threading

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import cgi
import codecs
import gzip
import operator
import os
import re
import urllib2
import urlparse
import logging
import pprint
import cssutils
from lxml import etree
from lxml.cssselect import CSSSelector


__all__ = ['PremailerError', 'Premailer', 'transform']


class PremailerError(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message)

class XMLSyntaxError(PremailerError):
    def __init__(self, message):
        super(PremailerError, self).__init__(message)

class CSS_SyntaxError(PremailerError):
    def __init__(self, message):
        super(PremailerError, self).__init__(message)

grouping_regex = re.compile('([:\-\w]*){([^}]+)}')


def merge_styles(old, new, class_=''):
    """
    if ::
      old = 'font-size:1px; color: red'
    and ::
      new = 'font-size:2px; font-weight: bold'
    then ::
      return 'color: red; font-size:2px; font-weight: bold'

    In other words, the new style bits replace the old ones.

    The @class_ parameter can be something like ':hover' and if that
    is there, you split up the style with '{...} :hover{...}'
    Note: old could be something like '{...} ::first-letter{...}'

    """

    def csstext_to_pairs(csstext):
        # if '!important' in csstext:
        #     csstext = csstext.replace('!important', '')
        parsed = cssutils.css.CSSVariablesDeclaration(csstext)
        for key in parsed:
            yield (key, parsed.getVariableValue(key))

    new_keys = set()
    news = []

    # The code below is wrapped in a critical section implemented via ``RLock``-class lock.
    # The lock is required to avoid ``cssutils`` concurrency issues documented in issue #65
    with merge_styles._lock:
        for k, v in csstext_to_pairs(new):
            news.append((k.strip(), v.strip()))
            new_keys.add(k.strip())

        groups = {}
        grouped_split = grouping_regex.findall(old)
        if grouped_split:
            for old_class, old_content in grouped_split:
                olds = []
                for k, v in csstext_to_pairs(old_content):
                    olds.append((k.strip(), v.strip()))
                groups[old_class] = olds
        else:
            olds = []
            for k, v in csstext_to_pairs(old):
                olds.append((k.strip(), v.strip()))
            groups[''] = olds

    # Perform the merge
    relevant_olds = groups.get(class_, {})
    merged = [style for style in relevant_olds if style[0] not in new_keys] + news
    groups[class_] = merged

    if len(groups) == 1:
        return '; '.join('%s:%s' % (k, v) for
                         (k, v) in sorted(groups.values()[0]))
    else:
        all = []
        for class_, mergeable in sorted(groups.items(),
                                        lambda x, y: cmp(x[0].count(':'),
                                                         y[0].count(':'))):
            all.append('%s{%s}' % (class_,
                                   '; '.join('%s:%s' % (k, v)
                                             for (k, v)
                                             in mergeable)))
        return ' '.join(x for x in all if x != '{}')

# The lock is used in merge_styles function to work around threading concurrency bug of cssutils library.
# The bug is documented in issue #65. The bug's reproduction test in test_premailer.test_multithreading.
merge_styles._lock = threading.RLock()


def make_important(bulk):
    """makes every property in a string !important.
    """
    return ';'.join('%s !important' % p if not p.endswith('!important') else p
                    for p in bulk.split(';'))


_element_selector_regex = re.compile(r'(^|\s)\w')
_cdata_regex = re.compile(r'\<\!\[CDATA\[(.*?)\]\]\>', re.DOTALL)
_importants = re.compile('\s*!important')
# These selectors don't apply to all elements. Rather, they specify
# which elements to apply to.
FILTER_PSEUDOSELECTORS = [':last-child', ':first-child', 'nth-child']


class Premailer(object):
    def __init__(self, html, base_url=None,
                 preserve_internal_links=False,
                 preserve_inline_attachments=True,
                 exclude_pseudoclasses=True,
                 keep_style_tags=False,
                 include_star_selectors=False,
                 remove_classes=True,
                 strip_important=True,
                 external_styles=None,
                 method="html",
                 base_path=None,
                 disable_basic_attributes=None,
                 disable_validation=False,
                 metadata=False
    ):
        self.html = html
        self.base_url = base_url
        self.preserve_internal_links = preserve_internal_links
        self.preserve_inline_attachments = preserve_inline_attachments
        self.exclude_pseudoclasses = exclude_pseudoclasses
        # whether to delete the <style> tag once it's been processed
        self.keep_style_tags = keep_style_tags
        self.remove_classes = remove_classes
        # whether to process or ignore selectors like '* { foo:bar; }'
        self.include_star_selectors = include_star_selectors
        if isinstance(external_styles, basestring):
            external_styles = [external_styles]
        self.external_styles = external_styles
        self.strip_important = strip_important
        self.method = method
        self.base_path = base_path
        if disable_basic_attributes is None:
            disable_basic_attributes = []
        self.disable_basic_attributes = disable_basic_attributes
        self.disable_validation = disable_validation
        self.metadata = metadata

    def _parse_style_rules(self, css_body, ruleset_index):
        leftover = []
        rules = []
        rule_index = 0
        FONT_FACE_RULE = 5
        # empty string
        if not css_body:
            return rules, leftover
        mylog = StringIO.StringIO()
        h = logging.StreamHandler(mylog)
        h.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
        cssutils.log.addHandler(h)
        cssutils.log.setLevel(logging.INFO)
        sheet = cssutils.parseString(css_body, validate=not self.disable_validation)
        assert sheet
        if mylog.getvalue():
            raise CSS_SyntaxError(mylog.getvalue())
        for rule in sheet:
            # handle media rule
            if rule.type == rule.MEDIA_RULE:
                leftover.append(rule)
                continue
            # handle font-face rule
            if rule.type == FONT_FACE_RULE and self.metadata == True:
                leftover.append(rule)
            # only proceed for things we recognize
            if rule.type != rule.STYLE_RULE:
                continue
            bulk = ';'.join(
                u'{0}:{1}'.format(key, rule.style[key])
                for key in rule.style.keys()
            )
            selectors = (
                x.strip()
                for x in rule.selectorText.split(',')
                if x.strip() and not x.strip().startswith('@')
            )
            for selector in selectors:
                if (':' in selector and self.exclude_pseudoclasses and
                                ':' + selector.split(':', 1)[1]
                        not in FILTER_PSEUDOSELECTORS):
                    # a pseudoclass
                    leftover.append((selector, bulk))
                    continue
                elif selector == '*' and not self.include_star_selectors:
                    continue

                # Crudely calculate specificity
                id_count = selector.count('#')
                class_count = selector.count('.')
                element_count = len(_element_selector_regex.findall(selector))

                specificity = (id_count, class_count, element_count, ruleset_index, rule_index)

                rules.append((specificity, selector, bulk))
                rule_index += 1

        return rules, leftover

    def transform(self, pretty_print=True, **kwargs):
        """change the self.html and return it with CSS turned into style
        attributes.
        """
        if etree is None:
            return self.html

        try:
            etree.fromstring(self.html)
        except etree.XMLSyntaxError as e:
            raise XMLSyntaxError(e)
            # for i in range(len(sys.exc_info())):
            #     print sys.exc_info()[i]
            # print sys.exc_type, " ", sys.exc_value

        if self.method == 'xml':
            parser = etree.XMLParser(ns_clean=False, resolve_entities=False)
        else:
            parser = etree.HTMLParser()
        stripped = self.html.strip().lower()
        tree = etree.fromstring(stripped, parser).getroottree()
        page = tree.getroot()

        # lxml inserts a doctype if none exists, so only include it in
        # the root if it was in the original html.
        root = tree if stripped.startswith(tree.docinfo.doctype) else page

        if page is None:
            print repr(self.html)
            raise PremailerError("Could not parse the html")
        assert page is not None

        # #
        # # style selectors
        # #

        rules = []
        index = 0

        for element in CSSSelector('style,link[rel~=stylesheet]')(page):
            # If we have a media attribute whose value is anything other than
            # 'screen', ignore the ruleset.

            media = element.attrib.get('media')
            if media and media != 'screen':
                continue

            is_style = element.tag == 'style'
            if is_style:
                css_body = element.text
            else:
                href = element.attrib.get('href')
                if not href:
                    continue

                # Try loading external style sheets and continue if not found
                try:
                    css_body = self._load_external(href)
                except ValueError:
                    continue

            these_rules, these_leftover = self._parse_style_rules(css_body, index)
            index += 1
            rules.extend(these_rules)

            parent_of_element = element.getparent()
            if these_leftover:
                if is_style:
                    style = element
                else:
                    style = etree.Element('style')
                    style.attrib['type'] = 'text/css'

                lines = []
                for item in these_leftover:
                    if isinstance(item, tuple):
                        k, v = item
                        lines.append('%s {%s}' % (k, make_important(v)))
                    # media rule
                    else:
                        FONT_FACE_RULE = 5
                        if item.type == FONT_FACE_RULE:
                            if self.metadata != True:
                                continue
                            if isinstance(item, cssutils.css.csscomment.CSSComment):
                                continue
                            for key in item.style.keys():
                                item.style[key] = (
                                    item.style.getPropertyValue(key, False),
                                    '!important'
                                )
                            lines.append(item.cssText)
                            continue
                        for rule in item.cssRules:
                            if isinstance(rule, cssutils.css.csscomment.CSSComment):
                                continue
                            for key in rule.style.keys():
                                rule.style[key] = (
                                    rule.style.getPropertyValue(key, False),
                                    '!important'
                                )
                        lines.append(item.cssText)
                style.text = '\n'.join(lines)

                if self.method == 'xml':
                    style.text = etree.CDATA(style.text)

                if not is_style:
                    element.addprevious(style)
                    parent_of_element.remove(element)

            elif not self.keep_style_tags or not is_style:
                parent_of_element.remove(element)

        if self.external_styles:
            for stylefile in self.external_styles:
                css_body = self._load_external(stylefile)
                these_rules, these_leftover = self._parse_style_rules(css_body, index)
                index += 1
                rules.extend(these_rules)

        # rules is a tuple of (specificity, selector, styles), where specificity is a tuple
        # ordered such that more specific rules sort larger.
        rules.sort(key=operator.itemgetter(0))

        first_time = []
        first_time_styles = []
        for __, selector, style in rules:
            new_selector = selector
            class_ = ''
            if ':' in selector:
                new_selector, class_ = re.split(':', selector, 1)
                class_ = ':%s' % class_
            # Keep filter-type selectors untouched.
            if class_ in FILTER_PSEUDOSELECTORS:
                class_ = ''
            else:
                selector = new_selector

            sel = CSSSelector(selector)
            for item in sel(page):
                old_style = item.attrib.get('style', '')
                if not item in first_time:
                    new_style = merge_styles(old_style, style, class_)
                    first_time.append(item)
                    first_time_styles.append((item, old_style))
                else:
                    new_style = merge_styles(old_style, style, class_)
                item.attrib['style'] = new_style
                self._style_to_basic_html_attributes(item, new_style,
                                                     force=True)

        # Re-apply initial inline styles.
        for item, inline_style in first_time_styles:
            old_style = item.attrib.get('style', '')
            if not inline_style:
                continue
            new_style = merge_styles(old_style, inline_style, class_)
            item.attrib['style'] = new_style
            self._style_to_basic_html_attributes(item, new_style, force=True)

        if self.remove_classes:
            # now we can delete all 'class' attributes
            for item in page.xpath('//@class'):
                parent = item.getparent()
                del parent.attrib['class']

        ##
        ## URLs
        ##
        if self.base_url:
            for attr in ('href', 'src'):
                for item in page.xpath("//@%s" % attr):
                    parent = item.getparent()
                    if attr == 'href' and self.preserve_internal_links \
                            and parent.attrib[attr].startswith('#'):
                        continue
                    if attr == 'src' and self.preserve_inline_attachments \
                            and parent.attrib[attr].startswith('cid:'):
                        continue
                    if not self.base_url.endswith('/'):
                        self.base_url += '/'
                    parent.attrib[attr] = urlparse.urljoin(self.base_url,
                                                           parent.attrib[attr].lstrip('/'))

        kwargs.setdefault('method', self.method)
        kwargs.setdefault('pretty_print', pretty_print)
        out = etree.tostring(root, **kwargs)
        if self.method == 'xml':
            out = _cdata_regex.sub(lambda m: '/*<![CDATA[*/%s/*]]>*/' % m.group(1), out)
        if self.strip_important:
            out = _importants.sub('', out)

        ### collect metadata instead ###
        if self.metadata:
            return out, self._detect_tags(out)
        ################################

        return out

    def _load_external_url(self, url):
        r = urllib2.urlopen(url)
        _, params = cgi.parse_header(r.headers.get('Content-Type', ''))
        encoding = params.get('charset', 'utf-8')
        if 'gzip' in r.info().get('Content-Encoding', ''):
            buf = StringIO.StringIO(r.read())
            f = gzip.GzipFile(fileobj=buf)
            out = f.read().decode(encoding)
        else:
            out = r.read().decode(encoding)
        return out

    def _load_external(self, url):
        """loads an external stylesheet from a remote url or local path
        """
        if url.startswith('//'):
            # then we have to rely on the base_url
            if self.base_url and 'https://' in self.base_url:
                url = 'https:' + url
            else:
                url = 'http:' + url

        if url.startswith('http://') or url.startswith('https://'):
            css_body = self._load_external_url(url)
        else:
            stylefile = url
            if not os.path.isabs(stylefile):
                stylefile = os.path.abspath(
                    os.path.join(self.base_path or '', stylefile)
                )
            if os.path.exists(stylefile):
                with codecs.open(stylefile, encoding='utf-8') as f:
                    css_body = f.read()
            elif self.base_url:
                url = urlparse.urljoin(self.base_url, url)
                return self._load_external(url)
            else:
                raise ValueError(u"Could not find external style: %s" %
                                 stylefile)

        return css_body

    def _style_to_basic_html_attributes(self, element, style_content,
                                        force=False):
        """given an element and styles like
        'background-color:red; font-family:Arial' turn some of that into HTML
        attributes. like 'bgcolor', etc.

        Note, the style_content can contain pseudoclasses like:
        '{color:red; border:1px solid green} :visited{border:1px solid green}'
        """
        if style_content.count('}') and \
                        style_content.count('{') == style_content.count('{'):
            style_content = style_content.split('}')[0][1:]

        attributes = {}
        for key, value in [x.split(':') for x in style_content.split(';')
                           if len(x.split(':')) == 2]:
            key = key.strip()

            if key == 'text-align':
                attributes['align'] = value.strip()
            elif key == 'background-color':
                attributes['bgcolor'] = value.strip()
            elif key == 'width' or key == 'height':
                value = value.strip()
                if value.endswith('px'):
                    value = value[:-2]
                attributes[key] = value
            # else:
            #     print "key", repr(key)
            #     print 'value', repr(value)

        for key, value in attributes.items():
            if key in element.attrib and not force or key in self.disable_basic_attributes:
                # already set, don't dare to overwrite
                continue
            element.attrib[key] = value

    def _detect_tags(self, tree):
        """find tags within html and return True or False for each tag
        add declarations instead of True for rules within the style tag
        """

        # create xml element tree using input
        # make input html all lower case for finding/matching

        if etree is None:
            return

        if self.method == 'xml':
            parser = etree.XMLParser(ns_clean=False, resolve_entities=False)
        else:
            parser = etree.HTMLParser()
        stripped = self.html.strip().lower()
        tree = etree.fromstring(stripped, parser).getroottree()

        # tree = etree.fromstring(html.lower())

        # Make a Dictionary of detected tags
        detected = {}
        # List of keys
        #   Button-Element = <button></button>
        #   Button-Attribute = <input type="button" />
        detected_names = "style", "script", "button-element", "button-attribute", "@media", "@font-face"

        # Find tags
        style = tree.xpath('//style')
        script = tree.xpath('//script')
        button = tree.xpath('//button')
        type_button = tree.xpath('//input[@type="button"]')

        # Find specified rules in style tag(s)
        media_rules = []
        fontface_rules = []
        media_type = 4
        fontface_type = 5
        # at least one style tag
        if len(style) >= 1:
            for style_index in range(len(style)):
                # mylog = StringIO.StringIO()
                # h = logging.StreamHandler(mylog)
                # h.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
                # cssutils.log.addHandler(h)
                # cssutils.log.setLevel(logging.INFO)
                style_sheet = cssutils.parseString(style[style_index].text, validate=False)
                # if mylog.getvalue():
                #     raise PremailerError('Errors detected.  Aborting metadata collection.')

                for rule in style_sheet:
                    if rule.type != fontface_type and rule.type != media_type:
                        continue

                    rule_text = rule.cssText
                    #rule_text = rule_text.replace('!important', '')
                    # remove beginning of rule (definition) from rule string
                    #   exposing the selectors and their declarations
                    rule_definition, rule_text = rule_text.split('{', 1)
                    rule_definition.strip()

                    if rule.type == fontface_type:
                        this_rule = {}
                        rule_text = rule_text.replace('}', '')

                        for property, value in [x.split(':') for x in rule_text.split(';')
                                           if len(x.split(':')) == 2]:
                            property = property.strip()
                            value = value.strip()
                            this_rule[property] = value
                        fontface_rules.append(this_rule)

                    if rule.type == media_type:
                        this_rule = {}

                        # remove @media from the rest of the definition
                        rule_declaration = rule_definition.split(' ', 1)[1]
                        rule_declaration = rule_declaration.strip()

                        selector = ''
                        selectors = []
                        media_elements = rule_text.split('{')

                        for element in media_elements:
                            selector_dictionary = {}

                            if not element:
                                continue

                            if not '}' in element:
                                # it must be a selector!
                                selector = element.strip()
                                continue

                            # remove next selector, leaving declarations
                            declaration_text, leftover = element.split('}', 1)
                            declaration_text = declaration_text.strip()

                            declarations = []
                            for property, value in [x.split(':') for x in declaration_text.split(';')
                                           if len(x.split(':')) == 2]:
                                this_declaration = {}
                                property, value = property.strip(), value.strip()
                                this_declaration[property] = value
                                declarations.append(this_declaration)

                            selector_dictionary[selector] = declarations
                            selectors.append(selector_dictionary)

                            # set next selector
                            selector = leftover.replace('}', '').strip()

                        this_rule[rule_declaration] = selectors
                        media_rules.append(this_rule)

        # create results list of tags and rules
        tags = style, script, button, type_button, media_rules, fontface_rules

        # Detect tags, adding boolean value for each tag to detected list
        # If style rules True, add list of declarations
        detected_count = 0
        for tag in tags:
            this_name = detected_names[detected_count]
            if len(tag) >= 1:
                if this_name == '@media':
                    detected[this_name] = media_rules
                    detected_count += 1
                    continue
                if this_name == '@font-face':
                    detected[this_name] = fontface_rules
                    detected_count += 1
                    continue

                # Add Dictionary
                detected[this_name] = True
            else:
                # Add Dictionary
                detected[this_name] = False
            detected_count += 1

        return detected


def transform(html, base_url=None):
    return Premailer(html, keep_style_tags=True,
                     remove_classes=False,
                     strip_important=False,
                     metadata=True).transform()



if __name__ == '__main__':
    html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @media screen {
            html {
                background: #fffef0;
                color: #300;
            }
            body {
                background-color: lightblue;
            }
            head {
                background-color: purple;
            }
        }
        p.footer { font-size: 1px}
        </style>
        <style>
        @media screen, projection {
            html {
                background: #fffef0;
                color: #300;
            }
            body {
                max-width: 35em;
                margin: 0 auto;
            }
        }

        @media print {
            html {
                background: #fff;
                color: #000;
            }
            body {
                padding: 1in;
                border: 0.5pt solid #666;
            }
        }
        @font-face {
            font-family: 'MyWebFont';
            src:    url('myfont.woff2') format('woff2'),
                    url('myfont.woff') format('woff');
        }
        @font-face {
            font-family: myFirstFont;
            src: url(sansation_bold.woff);
            font-weight: bold;
        }
        @font-face {
            font-family: mySecondFont;
            src: url(sansation_italic.woff);
            font-style: italic;
        }
        .testClass {
            font-family: 'Arial';
        }
        h1, h2 { color: red;  }
        strong {
          text-decoration:none
          }
        p { font-size:2px;
            width: 400px;
            }
        body {
            font-family: 'MyWebFont', Fallback, sans-serif;
        }

        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        <form>
        <input type="button" value="this is a text button"/>
        </form>
        </body>
        </html>"""
    p = Premailer(html)
    pp = pprint.PrettyPrinter(indent=2)
    t = transform(html)
    print "*** HTML with Inlined CSS ***\n"
    print t[0]
    print "*** CSS Metadata ***\n"
    print pp.pprint(t[1])
    # print transform(html)
    # print p._detect_tags(html)



