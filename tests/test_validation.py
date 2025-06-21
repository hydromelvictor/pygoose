import unittest
from src.pygoose import connect, disconnect, get_database


class TestDatabaseConnection(unittest.TestCase):
    def setUp(self):
        connect('mongodb://localhost:27017/connexion_test')

    def tearDown(self):
        disconnect()

    def test_connection(self):
        db = get_database()
        self.assertIsNotNone(db)
        self.assertEqual(db.name, 'connexion_test')


if __name__ == '__main__':
    unittest.main
