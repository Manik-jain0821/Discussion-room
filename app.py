from flask import Flask, url_for,redirect, session ,render_template ,request
# from app import app
import mysql.connector
from authlib.integrations.flask_client import OAuth
import os 
from datetime import datetime
from dotenv import load_dotenv
from mysql.connector.dbapi import NUMBER

import string    
import random # define the random module  


load_dotenv()  # take environment variables from .env.
#enviorment variables
# print(os.getevn("PATH"))

app = Flask(__name__)


# # ----- CLASSES --------

class user:
    def __init__(self,id,name,department,phone):
        self.id = id
        self.name = name
        self.department = department
        self.phone = phone

class user_data:
    def __init__(self,email,firstname,lastname,contact):
        self.firstname=firstname
        self.lastname=lastname
        self.email=email
        self.contact = contact

class create_clas:
    def __init__(self,email,course_name,class_name,course_code,teacher_name,join_code):
        self.email = email
        self.class_name = class_name
        self.course = course_name 
        self.teacher = teacher_name
        self.course_code = course_code
        self.join_code = join_code

class new_class:
    def __init__(self,role,email,class_name,course_code,course_name,name,date,join_code):
        self.email = email
        self.role = role
        self.date = date
        self.class_name = class_name
        self.course = course_name 
        self.name = name
        self.course_code = course_code
        self.join_code = join_code


class class_data:
    def __init__(self,role,email,class_name,course_code,course_name,name,date,join_code):
        self.email = email
        self.role=role
        self.class_name = class_name
        self.course = course_name 
        self.name = name
        self.course_code = course_code
        self.date = date
        self.join_code = join_code

class announcement:
    def __init__(self,time,join_code,announce,ancid,name):
        self.name = name
        self.time = time
        self.join_code = join_code
        self.announce = announce
        self.ancid = ancid
        
class participants:
    def __init__(self,role,email,name):
        self.name = name
        self.role = role
        self.email = email

# configure db
mydb = mysql.connector.connect(
host =  os.getenv("mysql_host"),
user =  os.getenv("mysql_user"),
password =  os.getenv("mysql_password"),
database = os.getenv("mysql_db"))
# print(mydb)
# app.config['MYSQL_DB'] = 'flaskapp1'
# app.config['MMYSQL_CURSORCLASS'] = 'DictCursor'

# mysql = MySQL(app)
# # # Oauth data
oauth = OAuth(app) 
app.secret_key= '9878753048'

Client_id = os.getenv("Client_id")
Client_secret = os.getenv("Client_secret")

list1 = ['USA', "UE", "IND", "UAE"]

google = oauth.register(
    name='google',
    client_id=Client_id,
    client_secret=Client_secret,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    acess_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope':'openid profile email'},   
)

@app.route('/url_query')
def example_request():
    # name = dict(session).get('name',None)
    name= request.args.get('name')
    mood = request.args.get('mood')
    return f'{name} is {mood}' 

@app.route('/',methods = ["POST","GET"]) 
def index():
    fname = dict(session).get('firstname',None)
    val1 = 'SignUp'
    classes=[]
    value =  url_for( 'login' ) 
    if "email" in session and "firstname" in session:
        cur = mydb.cursor()
        fname = fname.upper()
        val1 = 'LogOut'
        value =  url_for( 'logout' ) 
        cur.execute("SELECT * FROM join_class where email =%s",[session["email"]])
        users = []
        users = cur.fetchall()
        cur.execute("commit")
        print(users)
        if len(users):
            for i in range(0,len(users)):
                classes.append(class_data(users[i][0],users[i][1],users[i][2],users[i][3],users[i][4],users[i][5],users[i][6],users[i][7]))  
                
    return render_template("index.html",fname=fname,val=value,val1=val1,classes=classes)
    # else:
    #     return redirect('/login')


@app.route('/login1',methods = ["POST","GET"]) 
def login1():
    if "email" in session:
        if "firstname" in session:
            return redirect('/')
        else:
            cur = mydb.cursor()
            cur.execute("SELECT * from user_data where email =%s",[session["email"]])
            userdetails = cur.fetchall()
            # print(userdetails[0][1])
            if len(userdetails) >0:
                session["email"]=userdetails[0][0]
                session["firstname"]=userdetails[0][1]
                session["lastname"]=userdetails[0][2]
                return redirect('/')
            else:
                if request.args.get('fname'):
                    fname = request.args.get('fname')
                    lname = request.args.get('lname')
                    # print(fname+"manik")
                    # lname = request.form'lname']
                    session["firstname"]=fname
                    session["lastname"]=lname
                    cur.execute("""INSERT INTO user_data(email,firstname,lastname) values(%s,%s,%s)""",(session["email"] ,session["firstname"],session["lastname"]))
                    mydb.commit()
                    print('done')
                    return redirect("/")
                else:
                    return render_template("login1.html")
                    
    else:
        return redirect("/login")            

@app.route('/login',methods= ["POST","GET"])
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/about')
def about():
    # google = oauth.create_client('google')
    # redirect_uri = url_for('authorize', _external=True)
    # return google.authorize_redirect(redirect_uri)
    return render_template("about.html",li=list1)

@app.route('/contact')
def contact():
    # google = oauth.create_client('google')
    # redirect_uri = url_for('authorize', _external=True)
   # return google.authorize_redirect(redirect_uri)
    email = dict(session).get('email',None)
    return render_template("contact.html",email=email)

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    # resp.raise_for_status()
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    if not 'lastname' in session:
        return redirect('/login1')
    return redirect('/')

@app.route('/add_stud',methods=["GET","POST"])
def add_stud():
    cur = mydb.cursor()
    try:
        if request.args.get("code"):
            code = request.args.get("code")
            print(code)
            session['code'] = code
            return redirect('/announce')
        
    except:
        print("code")

    if "email" in session:
        if request.args.get("joincode"):
            join = request.args.get("joincode")
            print("join")
            name = session["firstname"]+' '+session['lastname']
            cur.execute("""insert into join_class (role,email,class_name,course_name,name,date,join_code) values('student',%s,(select class_name from create_class where join_code= %s),(select course_name from create_class where join_code= %s),(select teacher from create_class where join_code= %s),(select date from create_class where join_code= %s),%s) """,[session['email'],join,join,join,join,join])
            cur.execute("commit")
            # print(join)
            return redirect("/add_stud")
        
        # print("data")
        cur.execute("SELECT * FROM join_class where email =%s",[session["email"]])
        users = []
        users = cur.fetchall()
        cur.execute("commit")
        classes=[]
        # print(users)
        if len(users):
            for i in range(0,len(users)):
                classes.append(new_class(users[i][0],users[i][1],users[i][2],users[i][3],users[i][4],users[i][5],users[i][6],users[i][7]))
        return render_template("add_stud.html",classes = classes,fname=session['firstname']+ ' ' +session['lastname'],email = session['email'])
    else:
        return redirect("/login")

        
    # except:
    #     print("not join")

    return redirect("/add_stud")
        


@app.route('/profile',methods = ["GET","POST"])
def change_profile():
    cur = mydb.cursor()
    try:
        if request.method == "POST":
            # request.form['last_name']
            # request.form['Contact']
            print("begin")
            cur.execute(" UPDATE user_data set firstname=%s,lastname=%s,contact=%s where email=%s",(request.form['first_name'],request.form['last_name'],str(request.form['contact']),session['email']))
            cur.execute("commit")
            print("doned")
            return redirect('/profile')   
    except: 
        print('nothing')

    cur.execute("SELECT * FROM join_class where email =%s",[session["email"]])
    users = []
    users = cur.fetchall()
    cur.execute("commit")
    classes = []
    if len(users):
        for i in range(0,len(users)):
            classes.append(class_data(users[i][0],users[i][1],users[i][2],users[i][3],users[i][4],users[i][5],users[i][6],users[i][7]))  
        
    cur.execute("select * from user_data where email =%s",[session['email']])
    users = cur.fetchall()
    fname = session['firstname']
    user=[]
    for i in range(0,len(users)):
        if users[i][3]:
            user.append(user_data(users[i][0],users[i][1],users[i][2],(users[i][3])))
        else:
            user.append(user_data(users[i][0],users[i][1],users[i][2],int()))
            
    # print(users)
    return render_template("profile.html",user=user,fname=fname.upper(),classes=classes)        
    



@app.route('/users',methods=["GET","POST"])
def users():
    if "email" in session:    
        cur = mydb.cursor()
        cur.execute("SELECT * FROM user_data")
        users = cur.fetchall()
        user=[]
        for i in range(0,len(users)):
            user.append(user_data(users[i][0],users[i][1],users[i][2]))
        # if request.method == "GET":
            # try:
            #     # delete_id = request.args.get('email')
            #     delete_id = request.args.get('email') 
            #     cur = mydb.cursor()
            #     cur.execute("""DELETE FROM %s where email=%s """ %(user_data,delete_id))
            #     cur.commit()
            #     cur.execute("commit")

            # except:
            #     print("request failed")

        return render_template('users.html',users=user)
    else:    
        redirect('/login')
        return render_template('users.html')

# @app.route('/stud',method=['POST',"GET"])
# def stud_info():
        
@app.route('/class',methods=["POST","GET"])
def class_info():
    if "email" in session:
        cur = mydb.cursor()
        cur.execute(    )
    else:
        redirect("/login")

@app.route('/classes',methods=["POST","GET"])
def create_class():
    if "email" in session:
        cur = mydb.cursor()
        # print("data")
        cur.execute("SELECT * FROM join_class where email =%s",[session["email"]])
        users = []
        users = cur.fetchall()
        cur.execute("commit")
        classes=[]
        # print(users)
        if len(users):
            for i in range(0,len(users)):
                classes.append(class_data(users[i][0],users[i][1],users[i][2],users[i][3],users[i][4],users[i][5],users[i][6],users[i][7]))  
            return render_template("base.html",classes=classes,fname=session['firstname'])
        else:
            return render_template("base.html",fname=session['firstname'])
    else:
        redirect("/login")
        
@app.route('/announce',methods=["POST","GET"])
def announc():
    cur = mydb.cursor()
    try:
        if request.method == "GET":
            annc = request.args.get("anc")
            now = datetime.now()
            # time = str(now.day + ","+now.month)
            # print(time)
            time = str(now.day)+','+str(now.strftime('%B'))+' '+ str(now.hour)+':'+str(now.minute)
            # print(time)
            time_post =str(datetime.now()) 
            # render_template('annouuncement.html')
            ancid = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 15))
            if annc:
                cur.execute("INSERT into announcement (name,post_time,join_code,announce,ancid,time,email) values(%s,%s,%s,%s,%s,%s,%s) ",[session['firstname'] + ' '+session['lastname'],time,session['code'],annc,ancid,now,session['email']])
                print(ancid,annc)
               
    except:
        print("not posted")

    if "email" in session:
        cur = mydb.cursor()
        cur.execute("SELECT * from announcement where join_code = %s order by time desc",[session['code']])
        anc_data =[]
        anc_data = cur.fetchall()
        cur.execute("commit")
        showanc = []
        for i in range(0,len(anc_data)):
            showanc.append(announcement(anc_data[i][0],anc_data[i][1],anc_data[i][2],anc_data[i][3],anc_data[i][4]))


        cur.execute("SELECT * from join_class where date = (SELECT date from class_join where join_code =%s) and role = 'teacher' ",[session["code"]])
        data = []
        data = cur.fetchall()
        cur.execute("commit")
        dataset=[]
        # print(data)
        for i in range(0,len(data)):
            dataset.append(class_data(data[i][0],data[i][1],data[i][2],data[i][3],data[i][4],data[i][5],data[i][6],data[i][7]))
        cur.execute("SELECT * FROM join_class where email =%s",[session["email"]])
        users = []
        users = cur.fetchall()
        cur.execute("commit")
        classes=[]
        # print(users)
        if len(users):
            for i in range(0,len(users)):
                classes.append(class_data(users[i][0],users[i][1],users[i][2],users[i][3],users[i][4],users[i][5],users[i][6],users[i][7]))  
            return render_template("announcement.html",classes=classes,fname=session['firstname'] + ' ' + session['lastname'],info = dataset,showanc=showanc)
    
        return render_template("announcement.html",fname=session['firstname'] + ' ' + session['lastname'])

        

@app.route('/members')
def members():
    cur = mydb.cursor()
    if 'code' in session:
        cur.execute("SELECT * from join_class where date = (SELECT date from class_join where join_code =%s and role='teacher') ",[session["code"]])
        data = []
        data = cur.fetchall()
        cur.execute("commit")
        dataset=[]
        # print(data)
        for i in range(0,len(data)):
            dataset.append(class_data(data[i][0],data[i][1],data[i][2],data[i][3],data[i][4],data[i][5],data[i][6],data[i][7]))
        cur.execute("SELECT * FROM join_class where email =%s",[session["email"]])
        users = []
        users = cur.fetchall()
        cur.execute("commit")
        classes=[]
        # print(users)
        if len(users):
            for i in range(0,len(users)):
                classes.append(class_data(users[i][0],users[i][1],users[i][2],users[i][3],users[i][4],users[i][5],users[i][6],users[i][7]))
    
        cur.execute("SELECT * from join_class where join_code = %s ",[session['code']])
        member = []
        member = cur.fetchall()
        members = []
        for i in range(0,len(member)):
                members.append(participants(member[i][0],member[i][1],member[i][5]))
        
        return render_template("open_class.html",classes=classes,members = members,fname=session['firstname'] + ' ' + session['lastname'],info=dataset)
    


@app.route('/create_new',methods=["post"])
def create_new():
    if request.method == "POST":
        cur = mydb.cursor()
        class_name = request.form['class_name']
        course_name = request.form['course_name']
        teacher_name = session["firstname"]
        date = str(datetime.now())
        email = session["email"]
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))    
        print("The randomly generated string is : " + str(ran)) # print the random data  
        cur.execute(""" insert into create_class(email,class_name,course_name,teacher,date,join_code) values(%s,%s,%s,%s,%s,%s)""",(email,class_name,course_name,teacher_name,date,str(ran)))
        cur.execute("commit")
        # cur.execute("select course_code from create_class where (course_name =%s AND date =%s)",(course_name,date))
        # course_code = cur.fetchall()
        role = "teacher"
        # print(course_code[0][0])
        # code = int(course_code[0][0])
        cur.execute(""" insert into join_class (role,email,class_name,course_name,name,date,course_code,join_code) values(%s,%s,%s,%s,%s,%s,(select course_code from create_class where date = %s),(select join_code from create_class where date=%s))""",(role,email,class_name,course_name,teacher_name,date,date,date))
        mydb.commit()
        cur.execute("""  insert into class_join(date,join_code) values ((select date from create_class where date = %s),(select join_code from create_class where date = %s))""",(date,date))
        # cur.execute(""" insert into join_class (course_code) values(%d) where date =%s""",(int(code),date))
        # cur.close()
        print('done')
    return redirect("/classes")

    
    
    
    
    
    
    
    
    # # render_template("base.html")
    
    # if "email" in session:
    #     cur = mydb.cursor()
    #     try:
    #         if request.method == "POST":
    #             # cur = mydb.cursor()
    #             cur.execute("SELECT * FROM user_data where email =%s",[session["email"]])
    #             users = cur.fetchall()
    #             class_name = request.form['class_name']
    #             course_name = request.form['course_name']
    #             teacher_name = session["firstname"]
    #             date = str(datetime.now())
    #             email = session["email"]
    #             cur.execute(""" insert into create_class(email,class_name,course_name,teacher,date) values(%s,%s,%s,%s,%s)""",(email,class_name,course_name,teacher_name,date))
    #             mydb.commit()
    #             cur.execute("select course_code from create_class where (course_name =%s AND date =%s)",(course_name,date))
    #             course_code = cur.fetchall()
    #             role = "teacher"
    #             print(course_code[0][0])
    #             cur.execute(""" insert into join_class(role,email,class_name,course_code,course_name,name) values(%s,%s,%s,%d,%s,%s)""",(role,email,class_name,course_code[0][0],course_name,teacher_name))
    #             mydb.commit()
    #             # cur.close()
    #             print('done')
    #             return render_template("base.html")
    #     except:
    #         print("try again")
    #         #  insert into create_class(email,class_name,course_name,teacher,date) values('maniknahta@gmail.com','CSBS','FOM','manik','10/12/21');
    #         # create table create_class(email varchar(100),class_name varchar(100),course_name varchar(100),course_code int NOT NULL AUTO_INCREMENT primary key,teacher varchar(100),date varchar(100) unique key);
            

    #     print("data")
    #     cur.execute("SELECT * FROM create_class where email =%s",[session["email"]])
    #     users = []
    #     users = cur.fetchall()
    #     cur.execute("commit")
    #     classes=[]
    #     print(users)
    #     if len(users):
    #         for i in range(0,len(users)):
    #             classes.append(create_clas(users[i][0],users[i][1],users[i][2],users[i][3],users[0][4]))  
    #         return render_template("base.html",classes=classes)
    #     else:
    #         return render_template("base.html")
    # else:
    #     return redirect("/login")




    
    

@app.route('/delete', methods=['POST'])
def delete_entry():
    cur = mydb.cursor()
    email =request.form['entry_id']
    # db.execute("DELETE FROM user_data where email = %s",(email))
    # cur.execute("""DELETE FROM user_data WHERE email = '?'""" , (email))
    # db.commit()
    cur.execute("delete from user_data where email=:x1",[email])
    cur.execute("commit")
    # flash('Entry deleted')
    print(email)
    return redirect(url_for('users'))
    
@app.route('/logout') 
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
    

if __name__ == "__main__": 
    app.run(debug=True)
