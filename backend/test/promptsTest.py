import unittest

from werkzeug.security import generate_password_hash

from backend.prompts import store_to_db, store_all_to_db
from backend.models import Provider, Insurance, Patient, db
from backend.app import create_app

class TestPrompts(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_store_to_db_new_provider(self):
        json_obj = {'name': 'Dr. Smith', 'specialty': 'Cardiology'}
        patient = Patient(username='test', password='test')
        db.session.add(patient)
        db.session.commit()
        store_to_db(json_obj, Provider, patient)
        self.assertEqual(Provider.query.count(), 1)

    def test_store_to_db_existing_insurance(self):
        insurance = Insurance(company_name='Blue Cross', policy_number='123456')
        patient = Patient(username='test', password='test', insurances=[insurance])
        db.session.add(patient)
        db.session.commit()
        json_obj = {'company_name': 'Blue Cross', 'policy_number': '123456'}
        store_to_db(json_obj, Insurance, patient)
        self.assertEqual(Insurance.query.count(), 1)

    def test_store_all_to_db(self):
        json_obj = {
            'Provider': {'name': 'Dr. Smith', 'specialty': 'Cardiology'},
            'Insurance': {'company_name': 'Blue Cross', 'policy_number': '123456'}
        }
        patient = Patient(username='test', password='test')
        db.session.add(patient)
        db.session.commit()
        store_all_to_db(json_obj, patient)
        self.assertEqual(Provider.query.count(), 1)
        self.assertEqual(Insurance.query.count(), 1)

    def testing(self):
        result = generate_password_hash('password')
        print(result)


if __name__ == '__main__':
    unittest.main()