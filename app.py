from flask import Flask, render_template, request 
import pandas as pd
import numpy as np
import pickle
import sqlite3
from googletrans import Translator



model = pickle.load(open('model.pkl', 'rb'))
cv = pickle.load(open('tk.pkl', 'rb'))

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route('/login')
def login():
	return render_template('signin.html')

@app.route('/logon')
def logon():
	return render_template('signup.html')

@app.route("/signup")
def signup():
    
    
    name = request.args.get('username','')
    number = request.args.get('number','')
    email = request.args.get('email','')
    password = request.args.get('password','')

    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("insert into `detail` (`name`,`number`,`email`, `password`) VALUES (?, ?, ?, ?)",(name,number,email,password))
    con.commit()
    con.close()

    return render_template("signin.html")

@app.route("/signin")
def signin():

    mail1 = request.args.get('user','')
    password1 = request.args.get('password','')
    con = sqlite3.connect('signup.db')
    cur = con.cursor()
    cur.execute("select `name`, `password` from detail where `name` = ? AND `password` = ?",(mail1,password1,))
    data = cur.fetchone()

    if data == None:
        return render_template("signin.html")    

    elif mail1 == 'admin' and password1 == 'admin':
        return render_template("index.html")

    elif mail1 == str(data[0]) and password1 == str(data[1]):
        return render_template("index.html")
    else:
        return render_template("signin.html")

@app.route('/index')
def index():
   return render_template('index.html')



@app.route('/notebook')
def notebook():
	return render_template('notebook.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']

        
        translator = Translator()
        translated_message = translator.translate(message, src='auto', dest='en').text

        
        data = [translated_message]
        vectorizer = cv.transform(data).toarray()

        
        predictions = model.predict_proba(vectorizer)[0]  

        
        toxic_prob = round(predictions[0], 2)
        severe_toxic_prob = round(predictions[1], 2)
        obscene_prob = round(predictions[2], 2)
        threat_prob = round(predictions[3], 2)
        insult_prob = round(predictions[4], 2)
        identity_hate_prob = round(predictions[5], 2)

        
        return render_template('result.html',
                               toxic_prob=toxic_prob,
                               severe_toxic_prob=severe_toxic_prob,
                               obscene_prob=obscene_prob,
                               threat_prob=threat_prob,
                               insult_prob=insult_prob,
                               identity_hate_prob=identity_hate_prob)
        




if __name__ == '__main__':
   app.run()