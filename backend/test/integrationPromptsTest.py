import json
import unittest
from backend.prompts import store_to_db, store_all_to_db, plaintextIngressPrompt, get_prediction_object, \
    askAltheaPrompt1, askAltheaPrompt2
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

    def test_prediction_and_store(self):
        json_obj = get_prediction_object(
            plaintextIngressPrompt,
            "I need to see my Gynecologist, Dr Roxanne Smith, but I am in the process of switching insurance to Cigna."
        )
        print(json_obj)
        print(json_obj['questions_list'])
        patient = Patient(username='test', password='test')
        db.session.add(patient)
        db.session.commit()
        store_all_to_db(json_obj, patient)
        self.assertEqual(Provider.query.count(), 1)

    def test_ask_althea_1(self):
        patient = Patient(username='test', password='test')
        provider = Provider(name='Dr. Smith', specialty='GastroEnterologist', phone_number='1234567890',
                            email='drsmith@example.health')
        insurance = Insurance(company_name='Cigna', policy_number='123456')
        patient.providers.append(provider)
        patient.insurances.append(insurance)
        db.session.add(patient)
        db.session.commit()

        input_text = "I am moving across the country, but I need to keep getting my Inflectra medicine every 8 weeks."
        user_info = ""
        for provider in patient.providers:
            user_info += str(provider) + "\n"
        for insurance in patient.insurances:
            user_info += str(insurance) + "\n"
        json_obj = get_prediction_object(askAltheaPrompt1, input_text, user_info)
        print(json_obj)

    def test_ask_althea_2(self):
        patient = Patient(username='test', password='test')
        provider = Provider(name='Dr. Smith', specialty='GastroEnterologist', phone_number='1234567890',
                            email='drsmith@example.health')
        insurance = Insurance(company_name='Cigna', policy_number='123456')
        patient.providers.append(provider)
        patient.insurances.append(insurance)
        db.session.add(patient)
        db.session.commit()

        input_text = "I am moving across the country, but I need to keep getting my Inflectra medicine every 8 weeks."
        user_info = "My insurance is staying the same. I need help finding a new provider, I don't have one yet. My new address is 123 Main st, Boston, MA. "
        for provider in patient.providers:
            user_info += str(provider) + "\n"
        for insurance in patient.insurances:
            user_info += str(insurance) + "\n"
        json_obj = get_prediction_object(askAltheaPrompt2, input_text, user_info)
        print(json_obj)



if __name__ == '__main__':
    unittest.main()