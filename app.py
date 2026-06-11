from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "secret123"
# MongoDB Connection
client = MongoClient(
    "mongodb+srv://root:root@tech1.kglkjga.mongodb.net/?retryWrites=true&w=majority&appName=Tech1"
)

db = client["task_system"]
users = db["users"]
tasks = db["tasks"]


# ---------------- LOGIN ---------------- #

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/check', methods=['POST'])
def check():

    username = request.form['username']
    password = request.form['password']

    user = users.find_one({
        "username": username,
        "password": password
    })

    if not user:
        return "Invalid Username or Password"

    session['username'] = username
    session['role'] = user['role']

    if user['role'] == 'admin':
        return redirect('/admin')

    return redirect('/employee')


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- ADMIN PANEL ---------------- #

@app.route('/admin')
def admin():

    if 'username' not in session:
        return redirect('/')

    if session.get('role') != 'admin':
        return "Access Denied"

    all_tasks = list(tasks.find())
    all_users = list(users.find({"role": "employee"}))

    return render_template(
        'admin.html',
        tasks=all_tasks,
        users=all_users
    )


# ---------------- EMPLOYEE PANEL ---------------- #

@app.route('/employee')
def employee():

    if 'username' not in session:
        return redirect('/')

    if session.get('role') != 'employee':
        return "Access Denied"

    my_tasks = list(tasks.find({
        "assigned_to": session['username']
    }))

    return render_template(
        'employee.html',
        tasks=my_tasks,
        username=session['username']
    )


# ---------------- ADD USER ---------------- #

@app.route('/add_user', methods=['POST'])
def add_user():

    if session.get('role') != 'admin':
        return "Access Denied"

    username = request.form['username']
    password = request.form['password']

    existing_user = users.find_one({
        "username": username
    })

    if existing_user:
        return "User already exists"

    users.insert_one({
        "username": username,
        "password": password,
        "role": "employee"
    })

    return redirect('/admin')


# ---------------- DELETE USER ---------------- #

@app.route('/delete_user', methods=['POST'])
def delete_user():

    if session.get('role') != 'admin':
        return "Access Denied"

    users.delete_one({
        "username": request.form['username']
    })

    return redirect('/admin')




# ---------------- CREATE TASK ---------------- #

@app.route('/create_task', methods=['POST'])
def create_task():

    if session.get('role') != 'admin':
        return "Access Denied"

    assigned_to = request.form['assigned_to']

    user = users.find_one({
        "username": assigned_to,
        "role": "employee"
    })

    if not user:
        return "Assigned user does not exist or is not an employee"

    tasks.insert_one({
        "title": request.form['title'],
        "assigned_to": assigned_to,
        "status": "Pending",
        "priority": request.form['priority'],
        "due_date": request.form['due_date']
    })

    return redirect('/admin')
# ---------------- UPDATE STATUS ---------------- #

@app.route('/update_status/<task_id>', methods=['POST'])
def update_status(task_id):

    print("Task ID:", task_id)
    print("Status:", request.form['status'])

    tasks.update_one(
        {"_id": ObjectId(task_id)},
        {
            "$set": {
                "status": request.form['status']
            }
        }
    )

    return redirect('/employee')



if __name__ == '__main__':
    app.run(debug=True)