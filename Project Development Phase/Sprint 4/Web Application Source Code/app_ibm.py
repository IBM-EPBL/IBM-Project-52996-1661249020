import requests
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail,Message
from random import randint
import flask
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import sqlite3
# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "xFuTO1-WU-Eja_hVVIm4a_nxXz1Bgcor0jCJFGixKc7y"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


#load models at top of app to load into memory only one time
with open('loan_application_model_lr.pickle', 'rb') as f:
    clf_lr = pickle.load(f)
ss = StandardScaler()


genders_to_int = {'MALE':1,
                  'FEMALE':0}

married_to_int = {'YES':1,
                  'NO':0}

education_to_int = {'GRADUATED':1,
                  'NOT GRADUATED':0}

dependents_to_int = {'0':0,
                      '1':1,
                      '2':2,
                      '3+':3}

self_employment_to_int = {'YES':1,
                          'NO':0}                      

property_area_to_int = {'RURAL':0,
                        'SEMIRURAL':1, 
                        'URBAN':2}

app =flask.Flask(__name__)
mail=Mail(app)

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]=465
app.config["MAIL_USERNAME"]='redbeast6382@gmail.com'
app.config['MAIL_PASSWORD']='zpcqtjwlnljwnoag'                    #you have to give your password of gmail account
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
mail=Mail(app)
otp=randint(000000,999999)

app.secret_key = "#@universityflaskapp@#"

con = sqlite3.connect("database.db")
print("Database created successfully")
con.execute("create table if not exists customer(pid integer primary key, name text, email text, password text,status BOOLEAN)")
print("Table created successfully")
con.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute(
                "INSERT INTO customer(name,email,password) VALUES (?,?,?)", (name, email, password))
            con.commit()
            msg=Message(subject='OTP',sender='redbeast6382@gmail.com',recipients=[email])
            msg.body=str(otp)
            mail.send(msg)
            flash("Registered successfully", "success")
        except:
            con.rollback()
            print("catch")
            flash("Please try again", "danger")
        finally:
            return render_template('verify.html')
            con.close()
    else:
        return render_template("index.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM customer where email=? and password=?", (email, password))
        data = cur.fetchone()

        if data:
            session["email"] = data["email"]
            print("sent to home")
            return redirect(url_for("home"))

        else:
            flash("Username or Password is incorrect", "danger")
            print("not sent to home")
            return redirect(url_for("index"))


@app.route('/home',methods=['POST','GET'])
def home():
    return render_template("home.html")

@app.route('/loanapplication',methods=['POST','GET'])
def loanapplication():
    if flask.request.method == 'GET':
        return (flask.render_template('loanapplication.html'))
    
    if flask.request.method =='POST':
        
        #get input
        #gender as string
        genders_type = flask.request.form['genders_type']
        #marriage status as boolean YES: 1 , NO: 0
        marital_status = flask.request.form['marital_status']
        #Dependents: No. of people dependent on the applicant (0,1,2,3+)
        dependents = flask.request.form['dependents']
        #dependents = dependents_to_int[dependents.upper()]
        
        #education status as boolean Graduated, Not graduated.
        education_status = flask.request.form['education_status']
        #Self_Employed: If the applicant is self-employed or not (Yes, No)
        self_employment = flask.request.form['self_employment']
        #Applicant Income
        applicantIncome = float(flask.request.form['applicantIncome'])
        #Co-Applicant Income
        coapplicantIncome = float(flask.request.form['coapplicantIncome'])
        #loan amount as integer
        loan_amnt = float(flask.request.form['loan_amnt'])
        #term as integer: from 10 to 365 days...
        term_d = int(flask.request.form['term_d'])
        # credit_history
        credit_history = int(flask.request.form['credit_history'])
        # property are
        property_area = flask.request.form['property_area']
        #property_area = property_area_to_int[property_area.upper()]

        #create original output dict
        output_dict= dict()
        output_dict['Applicant Income'] = applicantIncome
        output_dict['Co-Applicant Income'] = coapplicantIncome
        output_dict['Loan Amount'] = loan_amnt
        output_dict['Loan Amount Term']=term_d
        output_dict['Credit History'] = credit_history
        output_dict['Gender'] = genders_type
        output_dict['Marital Status'] = marital_status
        output_dict['Education Level'] = education_status
        output_dict['No of Dependents'] = dependents
        output_dict['Self Employment'] = self_employment
        output_dict['Property Area'] = property_area
        


        x = np.zeros(21)
    
        x[0] = applicantIncome
        x[1] = coapplicantIncome
        x[2] = loan_amnt
        x[3] = term_d
        x[4] = credit_history
        # NOTE: manually define and pass the array(s) of values to be scored in the next line
        payload_scoring = {"input_data": [{"fields":  ['genders_type','marital_status','education_status','self_employment','applicantIncome','coapplicantIncome','an_amnt','term_d','credit_history','property_area'], "values":  ['genders_type','marital_status','education_status','self_employment','applicantIncome','coapplicantIncome','an_amnt','term_d','credit_history','property_area']}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/bb61da4a-5b79-4a71-972e-3751cf2ea93d/predictions?version=2022-11-20', json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
        # print("Scoring response")
        prediction=response_scoring.json()
        # predict=prediction['prediction'][0]['values'][0][0]
        print("Final prediction:",prediction)
        #render form again and add prediction
        return flask.render_template('loanapplication.html',original_input=output_dict,predict=prediction)

@app.route('/jointreport',methods=['POST','GET'])
def jointreport():
    return render_template("jointreport.html")

@app.route('/report',methods=['POST','GET'])
def report():
    return render_template("report.html")

@app.route('/verify',methods=["POST",'GET'])
def verify():
    user_otp=request.form['otp']
    if otp==int(user_otp):
        return render_template('confirm.html')
    return "<h3>Please Try Again</h3>"
    
if __name__ == '__main__':
    app.run(debug=True)
