import unittest

from premailer import Premailer, etree

class MyTestCase(unittest.TestCase):
    ### This section of unit tests is for @media queries ###
    def test_standard_media_query(self):
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {
            '@media': [{u'screen': [{u'html': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
                                    {u'body': [{u'background-color': u'lightblue'}]},
                                    {u'head': [{u'background-color': u'purple'}]}]}]
        }
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_media_query_with_print(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @media print {
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {
            '@media': [{u'print': [{u'html': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
                                    {u'body': [{u'background-color': u'lightblue'}]},
                                    {u'head': [{u'background-color': u'purple'}]}]}]
        }
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_media_query_with_max_width(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @media only screen and (max-width: 680px) {
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {
            '@media': [{u'only screen and (max-width: 680px)': [{u'html': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
                                    {u'body': [{u'background-color': u'lightblue'}]},
                                    {u'head': [{u'background-color': u'purple'}]}]}]
        }
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_multiple_media_queries_in_one_style_tag(self):
        html = u"""<html>
        <head>
        <title>Test</title>
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {
            '@media': [{u'screen, projection': [{u'html': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
            {u'body': [{u'max-width': u'35em'}, {u'margin': u'0 auto'}]}]},
            {u'print': [{u'html': [{u'background': u'#fff'}, {u'color': u'#000'}]},
            {u'body': [{u'padding': u'1in'}, {u'border': u'0.5pt solid #666'}]}]}]
        }
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_multiple_media_queries_in_two_style_tags(self):
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {
            '@media': [{u'screen': [{u'html': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
            {u'body': [{u'background-color': u'lightblue'}]}, {u'head': [{u'background-color': u'purple'}]}]},
            {u'screen, projection': [{u'html': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
            {u'body': [{u'max-width': u'35em'}, {u'margin': u'0 auto'}]}]},
            {u'print': [{u'html': [{u'background': u'#fff'}, {u'color': u'#000'}]},
            {u'body': [{u'padding': u'1in'}, {u'border': u'0.5pt solid #666'}]}]}]
        }
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_invalid_media_selector(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @media screen {
            monkey {
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {
            '@media': [{u'screen': [{u'monkey': [{u'background': u'#fffef0'}, {u'color': u'#300'}]},
                                    {u'body': [{u'background-color': u'lightblue'}]},
                                    {u'head': [{u'background-color': u'purple'}]}]}]
        }
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    ### This section of unit tests is for @Font-Face ###
    def test_standard_font_face(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        @font-face {
            font-family: myFirstFont;
            src: url(sansation_bold.woff);
            font-weight: bold;
        }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'@font-face': [{u'font-family': u'myfirstfont',
                    u'src': u'url(sansation_bold.woff)', u'font-weight': u'bold'}]}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_multiple_font_face_in_one_style_tag(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
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
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'@font-face': [{u'font-family': u'myfirstfont',
                    u'src': u'url(sansation_bold.woff)', u'font-weight': u'bold'},
                    {u'font-family': u'mysecondfont',
                    u'src': u'url(sansation_italic.woff)', u'font-style': u'italic'}]}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_multiple_font_face_in_two_style_tags(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
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
        </style>
        <style>
        @font-face {
            font-family: myThirdFont;
            src: url(sansation_normal.woff);
            font-weight: normal;
        }
        @font-face {
            font-family: myFourthFont;
            src: url(sansation_oblique.woff);
            font-style: oblique;
        }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'@font-face': [{u'font-family': u'myfirstfont',
                    u'src': u'url(sansation_bold.woff)', u'font-weight': u'bold'},
                    {u'font-family': u'mysecondfont',
                    u'src': u'url(sansation_italic.woff)', u'font-style': u'italic'},
                    {u'font-family': u'mythirdfont',
                    u'src': u'url(sansation_normal.woff)', u'font-weight': u'normal'},
                    {u'font-family': u'myfourthfont',
                    u'src': u'url(sansation_oblique.woff)', u'font-style': u'oblique'}]}

        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    # REMOVE THE FOLLOWING TEST?  RAISES ERROR

    # def test_invalid_font_face_property_name(self):
    #     # raising warning for Unknown Property name
    #     # font-famil
    #     html = u"""<html>
    #     <head>
    #     <title>Test</title>
    #     <style>
    #     @font-face {
    #         font-famil: myFirstFont;
    #         src: url(sansation_bold.woff);
    #         font-weight: bold;
    #     }
    #     </style>
    #     </head>
    #     <body>
    #     <h1>Hi!</h1>
    #     <p><strong>Yes!</strong></p>
    #     <p class="footer" style="color:red">Feetnuts</p>
    #     </body>
    #     </html>"""
    #
    #     expected = {'@font-face': [{u'font-famil': u'myfirstfont',
    #                 u'src': u'url(sansation_bold.woff)', u'font-weight': u'bold'}]}
    #     actual = Premailer(html, metadata=True).transform()
    #     self.assertDictContainsSubset(expected, actual[1])

    ### This section of unit tests is for HTML element detection ###
    def test_standard_button_tag(self):
        html = u"""<html>
        <head>
        <title>Test</title>

        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>

        <button>Click Me!</button>
        </body>
        </html>"""

        expected = {'button-element': True}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_input_button_tag(self):
        html = u"""<html>
        <head>
        <title>Test</title>

        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <input type="button" value="Clicky!"/>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'button-attribute': True}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_script_tag(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <script></script>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'script': True}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_style_tag(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>
        strong {
          text-decoration:none
          }
        p { font-size:2px;
            width: 400px;
            }
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'style': True}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    def test_false_cases(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'style': False, 'script': False, 'button-element': False,
                    'button-attribute': False, '@media': False, '@font-face': False}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

    ### This sectiion of unit tests is for miscellaneous scenarios ###
    def test_multiple_new_lines_in_css_rule(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style>



        @font-face {



            font-family: myFirstFont;

            src: url(sansation_bold.woff);




            font-weight: bold;

        }



        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>
        </body>
        </html>"""

        expected = {'style': True, '@font-face': [{u'font-family': u'myfirstfont',
                    u'src': u'url(sansation_bold.woff)', u'font-weight': u'bold'}]}
        actual = Premailer(html, metadata=True).transform()
        self.assertDictContainsSubset(expected, actual[1])

if __name__ == '__main__':
    unittest.main()