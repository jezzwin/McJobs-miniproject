from flask import Flask, render_template, request, redirect, url_for, session, send_file
from indeed_jobs_webscrapping import scrape_indeed_jobs
import re
import MySQLdb.cursors
import pdfkit

app = Flask(__name__)

db = MySQLdb.connect(
    host='localhost',
    user='root',
    password='',
    database='users',
    cursorclass=MySQLdb.cursors.DictCursor
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Query the database for the user with the entered email
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user and user['password'] == password:
            # Login successful, redirect to success page with username
            return redirect(url_for('success', username=user['username']))
        else:
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor()
        
        # Check if a user with the entered email already exists in the database
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = 'Email already registered. Please use a different email.'
            return render_template('signup.html', error_message=error_message)
        
        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        db.commit()
        
        # Signup successful, redirect to login page
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route('/success.html', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        username = request.form['username']
        return redirect(url_for('success', username=username))
    else:
        username = request.args.get('username')
        if username:
            return render_template('success.html', username=username)
        else:
            return redirect(url_for('login'))


@app.route('/about_us.html',methods=['GET', 'POST'])
def about_us():
    return render_template('about_us.html')

@app.route('/resume.html')
def resume_form():
    return render_template('resume.html')

@app.route('/resume_builder', methods=['POST'])
def resume_builder():
    # Retrieve form data
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    education = request.form['education']
    trainings = request.form['trainings']
    projects = request.form['projects']
    skills = request.form['skills']
    roles = request.form['roles']

    # Generate resume PDF using a suitable library
    # Example using pdfkit: Install the library using `pip install pdfkit` and configure the PDF rendering options
    pdfkit.from_string(
        render_template('resume_template.html', name=name, email=email, phone=phone, address=address,
                        education=education, trainings=trainings, projects=projects, skills=skills, roles=roles),
        'resume.pdf'
    )

    # Return the PDF as a downloadable response
    return send_file('resume.pdf')

@app.route('/scrape.html', methods=['GET', 'POST'])
def scrape():
    return render_template('scrape.html')

@app.route('/scrape', methods=['GET', 'POST'])
def scraperesults():
    if request.method == 'POST':
        job_title = request.form['job_title']
        location = request.form['location']
        html_table = scrape_indeed_jobs(job_title, location)
        return render_template('result.html', html_table=html_table)


if __name__ == '__main__':
    app.run(debug=True)
