import unittest
from premailer import Premailer, CSSSyntaxError, HTMLElementError


class MyTestCase(unittest.TestCase):
    # This section of unit tests is for CSS errors
    def test_CSS_missing_semicolon(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        p { font-size:2px
            width: 400px;
            }
        h1, h2 { color: red;  }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    def test_CSS_missing_colon(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color red;  }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    def test_CSS_missing_brace(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red;
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    def test_CSS_spelling_typo_value(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        p { font-size:2p;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    def test_CSS_spelling_typo_property(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        p { font-siz:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    def test_CSS_extra_random_characters(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style> * monkey */
        p { font-siz:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    def test_CSS_missing_required_quotes(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @font-face {
            font-family: 'MyWebFont';
            src:    url('myfont.woff2') format(woff2), /* no quotes here */
                    url('myfont.woff') format('woff');
        }
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(CSSSyntaxError):
            Premailer(html).transform()

    # This section of unit tests is for HTML errors
    def test_HTML_invalid_tag(self):
        html = u"""<html>
        <heads>
        <title>Test</title>
        <style>
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </heads>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(HTMLElementError):
            Premailer(html).transform()

    def test_HTML_invalid_matching_tags(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <!-- spelled incorrectly! -->
        <styles>
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </styles>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaises(HTMLElementError):
            Premailer(html).transform()

    # This section of unit tests is for multiple errors
    def test_CSS_missing_semicolon_and_colon(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        p { font-size 2px
            width: 400px;
            }
        h1, h2 { color: red;  }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaisesRegexp(CSSSyntaxError,
                                     'ERROR Property: "2px" Unexpected ident. '
                                     '\[3 - Line: 2, Column: 23'):
            Premailer(html).transform()

    def test_CSS_missing_semicolon_and_colon_and_invalid_matching_tags(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <styles>
        p { font-size 2px
            width: 400px;
            }
        h1, h2 { color: red;  }
        strong {
          text-decoration:none
          }
        </styles>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaisesRegexp(HTMLElementError,
                                     "Tag styles invalid, line 4, column 16"):
            Premailer(html).transform()

    def test_CSS_missing_required_quotes_and_invalid_rule(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @font-fac {
            font-family: 'MyWebFont';
            src:    url('myfont.woff2') format(woff2), /* no quotes here */
                    url('myfont.woff') format('woff');
        }
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaisesRegexp(CSSSyntaxError,
                                     'WARNING CSSStylesheet: '
                                     'Unknown @rule found: '
                                     '"@font-fac" - Line: 2, Column: 9'):
            Premailer(html).transform()

    # This section of unit tests is for specific warning exceptions
    def test_CSS_unknown_rule(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @page { size:8.5in 11in; margin: 2cm }
        @keyframes fadein {
                from { opacity: 0; }
                to   { opacity: 1; }
            }

            /* Firefox */
            @-moz-keyframes fadein {
                from { opacity: 0; }
                to   { opacity: 1; }
            }

            /* Safari and Chrome */
            @-webkit-keyframes fadein {
                from { opacity: 0; }
                to   { opacity: 1; }
            }

            /* Internet Explorer */
            @-ms-keyframes fadein {
                from { opacity: 0; }
                to   { opacity: 1; }
            }

            /* Opera */
            @-o-keyframes fadein {
                from { opacity: 0; }
                to   { opacity: 1; }
            }
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaisesRegexp(CSSSyntaxError, 'WARNING CSSStylesheet: '
                                     'Unknown @rule found'):
            Premailer(html).transform()

    def test_CSS_unknown_property(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        img {
            max-width: 600px;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
          }
        p { font-size:2px;
            width: 400px;
            }
        h1, h2 { color: red; }
        strong {
          text-decoration:none
          }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        with self.assertRaisesRegexp(CSSSyntaxError,
                                     'WARNING Property: '
                                     'Unknown Property name: '
                                     '"-ms-interpolation-mode"'):
            Premailer(html).transform()

if __name__ == '__main__':
    unittest.main()