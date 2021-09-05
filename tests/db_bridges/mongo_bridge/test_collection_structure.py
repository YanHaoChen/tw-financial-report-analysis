import unittest
from db_bridges.mongo_bridge.collection_structure import CollectionStructure


class FakeCollection(CollectionStructure):

    def set_name(self):
        return 'fake'

    def set_unique_fields(self):
        return {'a': int, 'b': str}

    def set_data_fields(self):

        return {'c': 1, 'd': 'hi'}


class IncompleteFakeCollection(CollectionStructure):

    def set_name(self):
        return 'fake'

    def set_unique_fields(self):
        return {'a': int, 'b': str}

    # without this
    # def set_data_fields(self):
    #     return {'c': 1, 'd': 'hi'}


class TestCollectionStructure(unittest.TestCase):

    def test_create_collection_structure_successfully(self):
        try:
            fake = FakeCollection()
            new_document = fake.document_operator(a=123, b='str', c=2)

            self.assertEqual(fake.name, 'fake')
            self.assertEqual(fake.unique_fields, {'a': int, 'b': str})
            self.assertEqual(fake.data_fields, {'c': 1, 'd': 'hi'})
            self.assertEqual(new_document, {
                'a': 123,
                'b': 'str',
                'c': 2,
                'd': 'hi'
            })

        except Exception as e:
            self.fail(f'Raise {e}. So The testing is fail.')

    def test_create_collection_structure_unsuccessfully(self):
        try:
            _ = IncompleteFakeCollection()
            self.fail(f'Except create fail')
        except TypeError as e:
            self.assertEqual(
                str(e),
                "Can't instantiate abstract class IncompleteFakeCollection with abstract methods set_data_fields"
            )
            pass
