import unittest
from rosdoc_lite import doxygenator as doxy

class TestGetDocPath(unittest.TestCase):

    def test_relative_doc_path(self):
        tag_pair = {'docs_url':"relative/path"}
        output = doxy.get_doc_path("sub/folders", tag_pair)
        self.assertEqual("../../relative/path", output)

        tag_pair = {'docs_url':"relative/path",'doxygen_output_folder':"doxygen_output_folder"}
        output = doxy.get_doc_path("sub/folders", tag_pair)
        self.assertEqual("../../relative/path/doxygen_output_folder", output)

    def test_absolute_doc_path(self):
        tag_pair = {'docs_url': "https://absolu.te/path"}
        output = doxy.get_doc_path("sub/folders", tag_pair)
        self.assertEqual("https://absolu.te/path", output)

        tag_pair = {'docs_url': "https://absolu.te/path",'doxygen_output_folder':"doxygen_output_folder"}
        output = doxy.get_doc_path("sub/folders", tag_pair)
        self.assertEqual("https://absolu.te/path/doxygen_output_folder", output)

