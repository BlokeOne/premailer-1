import unittest
import sys

from premailer import Premailer, etree, detect_tags

class Tests(unittest.TestCase):

    def test_metadata(self):
        html = u"""<html>
        <head>
        <title>Test</title>
        <style></style>
        <style>
        @media screen and (max-width: 300px) {
        body {
            background-color: lightblue;
            }
        }

        @font-face {
            font-family: myFirstFont;
            src: url(sansation_bold.woff);
            font-weight: bold;
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
        p.footer { font-size: 1px}
        </style>
        </head>
        <body>
        <h1>Hi!</h1>
        <p><strong>Yes!</strong></p>
        <p class="footer" style="color:red">Feetnuts</p>

        <input type="button" />
        </body>
        </html>"""
