from flask import Flask, render_template, request
from supabase import create_client
import pandas as pd
import numpy as np
import json
from email.message import EmailMessage
import ssl
import smtplib
import os
import string
from werkzeug.utils import secure_filename
import os

srt=''

app = Flask(__name__)
app.config['SECRET_KEY']='My super secret key'
url = "https://mjwonzcuwgpgaruqzrkw.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1qd29uemN1d2dwZ2FydXF6cmt3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODAzNDUyNTcsImV4cCI6MTk5NTkyMTI1N30.Ty31n59HklfH-eSMZSzlCw5hEk4yGoUEmI1ZgteUBCo"
supabase = create_client(url,key)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/Vendors")
def contact():
    return render_template("vendors.html")

@app.route("/table", methods=['POST','GET'])
def abe():
    response = supabase.table('data').select('*').execute().json()
    c = json.loads(response)
    l = pd.DataFrame(c['data'])
    mask=l['City'] == request.form['City']
    mask1 = l['Category'] == request.form['Category']
    final = l[mask & mask1]
    if final.empty == False:
        final = final.drop('Category', axis=1)
        final.rename(columns = {'Subcategory':'Category'}, inplace = True)
        final.index = np.arange(1,len(final)+1)
        final['Address'].replace(r'\s+|\\n', ' ', regex=True, inplace=True)
        final = final.style.set_table_styles([dict(selector='th,td', props=[('text-align', 'center'),('border-style','solid'),('border-width','1px')])])
        final.set_properties(**{'text-align': 'center'}).hide_index()
        success="List of GPCB verified vendors"
        return render_template('vendors.html', success=success,tables=[final.to_html(classes='data')], titles=final.columns.values)
    else:
        message="Sorry, no vendors found!!"
        return render_template('vendors.html', message=message)

@app.route("/inquiry",methods=['POST','GET'])
def jawab():
     if request.method == 'POST': 
         try:
             if request.form['email'] != '' and request.form['contact'] != '' and request.form['query'] != '':
                    f = request.files['file']
                    basepath = os.path.dirname(__file__)
                    upload_path = os.path.join(basepath, '',secure_filename(f.filename)) 
                    f.save(upload_path) 
                    v = request.form['query']
                    v.splitlines()
                    query = srt.join(v)
                    new = query.replace(" ", "")
                    new_string = new.translate(str.maketrans('', '', string.punctuation))
                    if f.filename.split(".")[-1] == 'jpg' or f.filename.split(".")[-1] == 'jpeg' or f.filename.split(".")[-1] == 'png':
                        resp=supabase.storage.from_("data").upload('name-{}'.format(new_string),upload_path,{"content-type":"image/jpeg"})
                    if f.filename.split(".")[-1] == 'pdf':
                        resp=supabase.storage.from_("data").upload('name-{}'.format(new_string),upload_path,{"content-type":"application/pdf"})
                    URL=supabase.storage.from_("data").get_public_url('name-{}'.format(new_string))
                    response = supabase.table('security').select("*").execute().json()
                    c = json.loads(response)
                    email_sender = 'shubh.bhatt67@gmail.com'
                    email_password = '{}'.format(c['data'][0]['password'])
                    email_receiver =['sasharma643@gmail.com','dhruvrajsinh251103@gmail.com']
                    subject = 'New query!!'
                    body = """
You have a new query from:

Email ID: {}
Mobile No: {}

Query:

{}

Document link:
{}
                            """.format(request.form['email'], request.form['contact'],request.form['query'],URL)
                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = email_receiver
                    em['Subject'] = subject
                    em.set_content(body)
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                        smtp.login(email_sender,email_password)
                        smtp.sendmail(email_sender,email_receiver,em.as_string())
                    email_receiver = [request.form['email']]
                    subject = 'Query recorded'
                    body = """
Thankyou for contacting remake waste management solutions. we have received your query and will get back to you soon.
                                """
                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = email_receiver
                    em['Subject'] = subject
                    em.set_content(body)
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                        smtp.login(email_sender,email_password)
                        smtp.sendmail(email_sender,email_receiver,em.as_string())
                    recorded="Query recorded!!! Thanks for contacting Remake "
                    return render_template('index.html',recorded=recorded)
             else:
                error="Please fill up all necessary details!!"
                return render_template('index.html',error=error)
        
         except:
            if request.form['email'] != '' and request.form['contact'] != '' and request.form['query'] != '':
                response = supabase.table('security').select("*").execute().json()
                c = json.loads(response)
                email_sender = 'shubh.bhatt67@gmail.com'
                email_password = '{}'.format(c['data'][0]['password'])
                email_receiver =['sasharma643@gmail.com','dhruvrajsinh251103@gmail.com']
                subject = 'New query!!'
                body = """
You have a new query from:

Email ID: {}
Mobile No: {}

Query:

{}
                        """.format(request.form['email'], request.form['contact'],request.form['query'])
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.sendmail(email_sender,email_receiver,em.as_string())
                email_receiver = [request.form['email']]
                subject = 'Query recorded'
                body = """
Thankyou for contacting remake waste management solutions. we have received your query and will get back to you soon.
                            """
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
                    smtp.login(email_sender,email_password)
                    smtp.sendmail(email_sender,email_receiver,em.as_string())
                recorded="Query recorded!!! Thanks for contacting Remake "
                return render_template('index.html',recorded=recorded)
            else:
                error="Please fill up all necessary details!!"
                return render_template('index.html',error=error)
    


@app.route("/subscriber",methods=['POST','GET'])
def subscriber():
    if request.form['email'] != '':
        
        response = supabase.table('security').select("*").execute().json()
        c = json.loads(response)
        email_sender = 'shubh.bhatt67@gmail.com'
        email_password = '{}'.format(c['data'][0]['password'])
        email_receiver =['sasharma643@gmail.com','dhruvrajsinh251103@gmail.com']
        subject = 'New Subscriber!!'
        body = """
You have a new subscriber :

Email ID: {}

                    """.format(request.form['email'])
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender,email_password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        email_receiver = [request.form['email']]
        subject = 'Query recorded'
        body = """
Thankyou for contacting remake waste management solutions. we have received your query and will get back to you soon.
                        """
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(email_sender,email_password)
            smtp.sendmail(email_sender,email_receiver,em.as_string())
        return render_template('index.html')
    else:
        error="Please fill up all necessary details!!"
        return render_template('index.html',error=error)

if __name__ =='__main__':
    app.run(host="0.0.0.0", port=5000)
