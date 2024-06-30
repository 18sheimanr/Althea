import json

from flask import redirect, request, session
from flask_login import login_required, logout_user, current_user, login_user

from app import app, db
from models import Patient, Provider, Insurance
from prompts import get_prediction_object, plaintextIngressPrompt, store_all_to_db, askAltheaPrompt1, askAltheaPrompt2


@app.route('/sign_out')
@login_required
def sign_out():
    logout_user()
    return {"success": True}, 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Patient.query.filter_by(username=request.json['username']).one()
        if user.verify_password(request.json['password']):
            login_user(user)
            return {"authenticated": current_user.is_authenticated}, 200
        else:
            return {"authenticated": current_user.is_authenticated}, 200


@app.route('/sign_up', methods=['POST'])
def sign_up():
    username = request.json['username']
    password = request.json['password']
    user = Patient.query.filter_by(username=username).first()
    if user:
        return {"error": "Username already exists"}, 400
    if len(password) < 8:
        return {"error": "Password must be at least 8 characters long"}, 400
    try:
        user = Patient(username=username, password=password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return {"error": str(e)}, 500
    user = Patient.query.filter_by(username=request.json['username']).one()
    login_user(user, remember=True, force=True)
    return {"username": user.username, "authenticated": current_user.is_authenticated}, 200


@app.route('/text_ingress', methods=['POST'])
def text_ingress():
    text = request.json['text']
    json_obj = get_prediction_object(plaintextIngressPrompt, text)
    store_all_to_db(json_obj, current_user)
    return {"text": text, "followupQuestions": json_obj.get("questions_list", [])}, 200


@app.route('/ask_althea', methods=['POST'])
def ask_althea():
    text = request.json['text']
    user_info = ""
    for provider in current_user.providers:
        user_info += str(provider) + "\n"
    for insurance in current_user.insurances:
        user_info += str(insurance) + "\n"
    json_obj = get_prediction_object(askAltheaPrompt1, text, user_info)
    return {"followupQuestions": json_obj.get("questions", [])}, 200


@app.route('/ask_althea_final_interaction', methods=['POST'])
def ask_althea_final_interaction():
    text = request.json['text']
    user_info = request.json['user_info']
    for provider in current_user.providers:
        user_info += str(provider) + "\n"
    for insurance in current_user.insurances:
        user_info += str(insurance) + "\n"
    json_obj = get_prediction_object(askAltheaPrompt2, text, user_info)

    return {"tasks": json_obj.get("tasks", [])}, 200


@app.route('/patient_info', methods=['GET'])
def patient_knowledge():
    patient = current_user
    providers = [str(provider) for provider in patient.providers]
    insurances = [str(insurance) for insurance in patient.insurances]
    combinedString = "\n".join(providers + insurances)
    return {"knowledge": combinedString}, 200
