from flask import Flask, render_template, request, url_for, flash, redirect, session
import sqlite3
import hashlib
import re

app = Flask(__name__)

connection = sqlite3.connect('parking.db')
connection.execute(
    'create table if not exists users (id integer primary key, name text not null, email text not null, password text not null)')
connection.execute(
    'create table if not exists parking_slot (id integer primary key, availability text not null)')
connection.execute('create table if not exists booking (id integer primary key , name text not null, email text not null, phone_number integer not null, license_number text not null, user_type text not null, parking_duration integer not null, slots integer not null )')

@app.route("/")
def main():
    return render_template('login.html')


@app.route("/booking", methods=['GET', 'POST'])
def booking():
    errors = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        slots = request.form['slots']
        phone = request.form['phone']
        license = request.form['license-plate']
        type = request.form['type']
        duration = request.form['parking-duration']
        slots = request.form['slots']
        if not name or not email or not phone or not license or not slots or not type or not duration:
            errors = 'Please Enter all the fields'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors = 'Your email is invalid. It should look like example@ex.com'
        else:
            errors = ""
        print ("test errors",errors)
        if not errors or errors == "":
            connection = sqlite3.connect('parking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("insert into booking(name , email , phone_number , license_number , user_type , parking_duration, slots ) values (?,?,?,?,?,?,?)",(name , email , phone , license , type , duration, slots ))
            connection.commit()
            connection2 = sqlite3.connect('parking.db')
            executing_cursor2 = connection2.cursor()
            executing_cursor2.execute("update parking_slot set availability = 'na' where slot_id = " + slots )

            # # added
            # connection2.row_factory = sqlite3.Row
            # cur = connection2.cursor()
            # print ("1")
            # cur.execute("select * from booking")
            # print ("2")
            # rows = cur.fetchall()
            # print ("3")
            # for row in rows:
            #     print(row['name'])
            # # added

            connection2.commit()
            return render_template("login.html")     
        else:
            errors = 'There is an issue with booking.'
        if not errors or errors == "":
            return render_template("index.html", name = name, email = email)     
        return render_template("index.html", name = name, email = email,errors = errors) 


@app.route("/home", methods=['GET', 'POST'])
def home():
    # return "Hello Flask"
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    errors = ''
    successMsg = ''
    print(f'in signup : {request.method}')
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        print(request.form)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if not name or not email or not password or not confirm_password:
            errors = 'Please Enter all the fields'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors = 'Your email is invalid. It should look like example@ex.com'
        elif not password == confirm_password:
            errors = "Both password and Confirmation password must be same."
        elif len(password) <= 4:
            errors = 'Your password must contain at least 5 characters.'
        else:
            errors = ""
        if not errors or errors == "":
            connection = sqlite3.connect('parking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("select * from users where email = ? and password = ? ", (email, password))
            toBeCreateduser = executing_cursor.fetchone()
            if not toBeCreateduser:
                executing_cursor.execute("insert into users (name, email, password) values (?, ?, ?)", (name, email, password))
                connection.commit()
                successMsg = 'Your account has been created successfully.'
                return render_template("login.html")
            else :
                errors = 'Looks like you already have an account with us.'
    return render_template("signup.html", errors = errors, successMsg = successMsg)
@app.route('/login', methods=['GET', 'POST'])
def login():
    errors = ''
    successMsg = ''
    print(f'in login : {request.form}')
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        print("ABCDEEEE", request.form)
        email = request.form['email']
        password = request.form['password']
        if 'user' in request.form:
            user = request.form['user']
            print(user)
        # role = request.form['role']
        if  not email or not password :
            errors = 'Please Enter all the fields'
        if  not user :
            errors = 'Please Enter a role'
        else:
            errors = ""
        if not errors or errors != "":
            connection = sqlite3.connect('parking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("select * from users where email = ? and password = ? ", (email, password))
            toBeCreateduser = executing_cursor.fetchone()
            print("ABC", toBeCreateduser)
            if not toBeCreateduser:
                errors = "The user does not exist please sign up first"
            connection2 = sqlite3.connect('parking.db')
            executing_cursor2 = connection2.cursor()
            executing_cursor2.execute("select * from booking")
            bookings = executing_cursor2.fetchmany()
            print("ABC", toBeCreateduser)
            if not toBeCreateduser:
                errors = "The user does not exist please sign up first"
            else:
                print(toBeCreateduser)
                if  user == "ADMIN":
                    return render_template("index.html", name = toBeCreateduser[1], email = toBeCreateduser[2], bookings = bookings, admin = "true" )
                else:
                    return render_template("index.html", name = toBeCreateduser[1], email = toBeCreateduser[2], bookings = bookings,admin = "false" )
    return render_template("login.html", errors=errors)


@app.route('/slotbooking', methods=['GET', 'POST'])
def slotbooking():
    connection = sqlite3.connect('parking.db')
    executing_cursor = connection.cursor()
    executing_cursor.execute('SELECT * FROM parking_slot WHERE availability ="a"')
    available_slots = executing_cursor.fetchall()

    return render_template("Book_now.html", name = request.args.get('name'), email = request.args.get('email'), available_slots = available_slots)

