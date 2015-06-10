import unittest
from premailer import Premailer, CSS_SyntaxError, XMLSyntaxError, HTMLElementError

class MyTestCase(unittest.TestCase):
    ### This section of unit tests is for CSS errors ###
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


        with self.assertRaises(CSS_SyntaxError):
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


        with self.assertRaises(CSS_SyntaxError):
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


        with self.assertRaises(CSS_SyntaxError):
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


        with self.assertRaises(CSS_SyntaxError):
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


        with self.assertRaises(CSS_SyntaxError):
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


        with self.assertRaises(CSS_SyntaxError):
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


        with self.assertRaises(CSS_SyntaxError):
            Premailer(html).transform()

    ### This section of unit tests is for HTML errors ###
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


        with self.assertRaises(XMLSyntaxError):
            Premailer(html).transform()

    def test_HTML_missing_closing_tag(self):
        html = u"""<html>
        <head>
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

        <!-- missing </head> -->

        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""


        with self.assertRaises(XMLSyntaxError):
            Premailer(html).transform()

    def test_HTML_missing_starting_tag(self):
        html = u"""<html>

        <!-- missing <head> -->

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

        </head> <!-- no starting tag for this -->

        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""


        with self.assertRaises(XMLSyntaxError):
            Premailer(html).transform()

    def test_HTML_invalid_matching_tags(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <styles> <!-- spelled incorrectly! -->
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

if __name__ == '__main__':
    unittest.main()