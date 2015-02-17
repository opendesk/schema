import os
import json
import unittest
import winnow
from winnow.models.base import WinnowVersion
from db import MockKVStore


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestValidateReferences(unittest.TestCase):


    def test_validate_refs(self):

        with open(os.path.join(DATA_DIR, "product_with_components.json"), "r") as f:
            product_dict = json.loads(f.read())

        winnow.validate(product_dict)


class TestExpandReferences(unittest.TestCase):

    def add_doc_at_data_path(self, path):

        with open(os.path.join(DATA_DIR, path), "r") as f:
            as_dict = json.loads(f.read())

        return WinnowVersion.add_doc(self.db, as_dict, {})


    def setUp(self):
        self.db = MockKVStore()


    def test_expand_refs(self):

        fine_sanding_process = self.add_doc_at_data_path("processes/fine-sanding/process.json")
        oiling_process = self.add_doc_at_data_path("processes/oiling/process.json")
        birch_ply_material = self.add_doc_at_data_path("birch-ply/material.json")
        wisa_material = self.add_doc_at_data_path("wisa-multiwall/material.json")
        premium_birch_ply = self.add_doc_at_data_path("finishes/premium-birch-ply/finish.json")
        processes = premium_birch_ply.get_doc()[u"options"][u"processes"]
        self.assertEqual(processes[u"type"], u'set::process')
        self.assertEqual(processes[u"values"], [{u'$ref': u'/processes/fine-sanding'}, {u'$ref': u'/processes/oiling'}])
        expanded = premium_birch_ply.expanded()
        expanded_sanding_value =  expanded.get_doc()[u"options"][u"processes"][u"values"][0]
        self.assertEqual(expanded_sanding_value, fine_sanding_process.get_doc())



    def test_expand_refs_with_options(self):

        fine_sanding_process = self.add_doc_at_data_path("processes/fine-sanding/process.json")
        oiling_process = self.add_doc_at_data_path("processes/oiling/process.json")
        birch_ply_material = self.add_doc_at_data_path("birch-ply/material.json")
        wisa_material = self.add_doc_at_data_path("wisa-multiwall/material.json")
        premium_birch_ply = self.add_doc_at_data_path("finishes/premium-birch-ply/finish.json")
        premium_wisa = self.add_doc_at_data_path("finishes/premium-wisa/finish.json")
        product_with_components = self.add_doc_at_data_path("product_with_components.json")

        expanded = product_with_components.expanded()
