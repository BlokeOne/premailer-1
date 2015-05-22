import unittest


class MyTestCase(unittest.TestCase):
    ### This section of unit tests is for @media queries ###
    def test_standard_media_query(self):
        self.assertEqual(True, True)

    def test_media_query_with_screen(self):
        self.assertEqual(True, True)

    def test_media_query_with_print(self):
        self.assertEqual(True, True)

    def test_media_query_with_max_width(self):
        self.assertEqual(True, True)

    def test_media_query_with_min_width(self):
        self.assertEqual(True, True)

    def test_media_query_with_projection(self):
        self.assertEqual(True, True)

    def test_multiple_media_queries_in_one_style_tag(self):
        self.assertEqual(True, True)

    def test_multiple_media_queries_in_two_style_tags(self):
        self.assertEqual(True, True)

    def test_blank_media_query(self):
        self.assertEqual(True, True)

    def test_invalid_media_selector(self):
        self.assertEqual(True, True)

    def test_nested_media_query(self):
        self.assertEqual(True, True)

    ### This section of unit tests is for @Font-Face ###
    def test_standard_font_face(self):
        self.assertEqual(True, True)

    def test_multiple_font_face_in_one_style_tag(self):
        self.assertEqual(True, True)

    def test_multiple_font_face_in_two_style_tags(self):
        self.assertEqual(True, True)

    def test_invalid_font_face_property_name(self):
        self.assertEqual(True, True)

    ### This section of unit tests is for HTML elements ###
    def test_standard_button_tag(self):
        self.assertEqual(True, True)

    def test_input_button_tag(self):
        self.assertEqual(True, True)

    def test_script_tag(self):
        self.assertEqual(True, True)

    def test_style_tag(self):
        self.assertEqual(True, True)

    ### This sectiion of unit tests is for miscellaneous scenarios ###
    def test_multiple_new_lines_in_css_rule(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
