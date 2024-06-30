import vertexai
from vertexai.generative_models import GenerativeModel
import json
from sqlalchemy.exc import SQLAlchemyError
from models import Provider, Insurance, db

vertexai.init(project="develop-251413", location="us-central1")

model = GenerativeModel(model_name="gemini-1.5-flash-001")

plaintextIngressPrompt = '''
You are an expert care navigator assistant. 
Given the following text in <USER_TEXT>, extract any fields that may be stored as rows in our database given the schema and return them in a JSON object. For any similar fields that the user is likely to know, and that would be helpful in coordinating their care, create a list of questions to ask the user so they may provide those fields, and include it as "questions_list" in the JSON. 
For example, given the following user text:
"I have only a prescription for 20mg of Lipitor I get prescribed from Dr. Smith. It is covered by Blue Cross of New England."
The JSON object should look like:
{
  "Provider": {
    "name": "Dr. Smith"
  },
  "Insurance": {
    "company_name": "Blue Cross of New England"
  }
  "questions_list": ["What is your insurance policy number?", "What is the best way to contact Dr. Smith?", "Is Dr. Smith your general practitioner or a specialist of some kind?"]
}

<DATABASE_SCHEMA>
class Provider(db.Model):
    name = db.Column(db.String(64), nullable=False, unique=True)
    specialty = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(255))
    preferred_contact = db.Column(db.String(20))

class Insurance(db.Model):
    company_name = db.Column(db.String(255))
    policy_number = db.Column(db.String(255))
    coverage_start_date = db.Column(db.Date)
    coverage_end_date = db.Column(db.Date)
    deductible = db.Column(db.Float)
    copay = db.Column(db.Float)
</DATABASE_SCHEMA>

<USER_TEXT>
{{input_text}}
</USER_TEXT>

**IMPORTANT please output ONLY the JSON object!
'''

askAltheaPrompt1 = '''
You are an expert healthcare navigator assistant. Given the following text in <USER_TEXT> along with the user's available information in <USER_INFO>, think about what you should do for the user.
Next, create a list of tasks the we may need to do to help them navigate care.
Next, if any of these tasks NECESSARILY REQUIRE more information, create a list of questions to ask the user. 
For example, given the following user text:
"I am moving across the country, but I need to keep getting my Inflectra medicine every 8 weeks."
{
    "thought": "I only need to know about new insurance and any new provider. We would need to call this new provider, give them insurance information, and ask for a referal for Inflectra after establishing care. However it is possible the user is not changing insurances, I should ask to confirm."
    "tasks": ["Determine new provider", "Transfer prescription to a new pharmacy", "Call new provider to establish care and get a referral for Inflectra."]
    "questions": ["Do you have a new insurance company, and if so, what are the details?", "Do you already have a new provider? If so, what is their name and best contact information?"]
}

<USER_INFO>
{{user_info}}
</USER_INFO>

<USER_TEXT>
{{input_text}}
</USER_TEXT>

**IMPORTANT please output ONLY a JSON object and NOTHING else! This output should be instantly parseable!
'''

askAltheaPrompt2 = '''
You are an expert healthcare navigator assistant. Given the following text in <USER_TEXT> along with their available information in <USER_INFO>, create a list of specific tasks, in chronological order, we need to navigate care. The tasks should be either a phone call, email, or in-person visit to a provider, pharmacy, or insurance company. Output only absolutely necessary tasks.
For example, given the following user text:
"I am moving across the country, but I need to keep getting my Inflectra medicine every 8 weeks."
And user information:
"New insurance: Blue Cross of New England, Policy Number: 123456. New Pharmacy: Keyes Drugs, phone: 617 731 7777. New provider: Dr. Smith, phone: 555-555-5555."
The output should look like this:
{
    "tasks": ["Call Dr. Smith to establish care, and provide them your new insurance.", "Call Blue Cross of New England to update your insurance information.", "Pickup Inflectra prescription from Keyes Drugs."]
}
<USER_INFO>
{{user_info}}
</USER_INFO>

<USER_TEXT>
{{input_text}}
</USER_TEXT>

**IMPORTANT please output ONLY a JSON object with field "tasks" and NOTHING else! This output should be instantly parseable!
'''


def store_to_db(json_obj, model, patient):
    # Check if an instance with the same name already exists
    instance = None
    if model == Provider:
        instance = Provider.query.filter_by(name=json_obj.get('name')).first()
    elif model == Insurance:
        instance = Insurance.query.filter_by(company_name=json_obj.get('company_name')).first()

    # If an instance does not exist, create a new one
    if instance is None:
        instance = model()

    # Iterate over the keys in the JSON object
    for key, value in json_obj.items():
        # If the key corresponds to an attribute in the model, set it
        if hasattr(instance, key):
            setattr(instance, key, value)

    # Add the new instance to the appropriate list in the patient object
    if isinstance(instance, Provider) and instance not in patient.providers:
        patient.providers.append(instance)
    elif isinstance(instance, Insurance) and instance not in patient.insurances:
        patient.insurances.append(instance)

    # Add the new instance to the session
    db.session.add(instance)

    # Try to commit the changes
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        # If an error occurs, roll back the session and print the error
        db.session.rollback()
        print(f"Error storing JSON as DB model: {e}")


def get_prediction_object(prompt, input_text, user_info=None):
    formatted_prompt = prompt.replace('{{input_text}}', input_text)
    if user_info:
        formatted_prompt = formatted_prompt.replace('{{user_info}}', user_info)
    response = model.generate_content(formatted_prompt).text
    cleaned_response = response.replace('\n', '').replace('\t', '').replace("json", "").replace("```", "").strip()
    print(cleaned_response)
    return json.loads(cleaned_response)


def store_all_to_db(json_obj, patient):
    store_to_db(json_obj.get('Provider', {}), Provider, patient)
    store_to_db(json_obj.get('Insurance', {}), Insurance, patient)
