from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_mysqldb import MySQL
import config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Your routes and other app setup here

app = Flask(__name__)
CORS(app)
app.secret_key = "b';\x90q\xe6x\x9c!iZxH\xa1\x81P\xe6f'"

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    usermailid=None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM User WHERE UserEmail_id=%s", [email])
        User = cur.fetchone()
        if User and check_password_hash(User[3], password):  # Assuming User table columns are id, email, password
            session['user_id'] = User[0]
            usermailid=User[2]
            session['usermailid'] = usermailid
            session.pop('selected_groups', None)
            session.pop('selected_recipients', None)
            return redirect(url_for('home',usermailid=usermailid))
        else:
            error = 'Invalid Credentials. Please try again.'
            return error
    return render_template('login.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)
        app.logger.info('Received POST request to add User: User_name - %s, UserEmail_id - %s, Passwordhash - %s', username, email, hashed_password)
        
        cur = mysql.connection.cursor()

        try:
            cur.execute("INSERT INTO User(User_name, UserEmail_id, Passwordhash) VALUES (%s, %s, %s)", (username, email, hashed_password))
            mysql.connection.commit()
            app.logger.info('User added successfully: User_name - %s, UserEmail_id - %s, Passwordhash - %s', username, email, hashed_password)
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            error = 'Registration failed. User already exists.'  # Set an error message
            app.logger.error('Error adding User to database: %s', str(e))
            return error
        finally:
            cur.close()

    return render_template('registration.html')

# @app.route('/home',methods=['POST'])
# def home():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
   
#     return render_template('home.html')

# @app.route('/home', methods=['POST'])
# def home():
#     selected_groups = request.form.getlist('groups[]')
#     # Now selected_groups contains the IDs of the selected groups
#     # Do whatever processing you need to do with these group IDs
#     return 'Selected groups: {}'.format(selected_groups)

from flask import render_template

# @app.route('/home',methods=['POST'])
# def home():
#     if 'user_id' in session:
#         # Assuming usermailid is passed to home.html
#         selected_groups = None  # Initialize selected_groups variable
#         usermailid=None
#         usermailid = request.args.get('usermailid')
#         if request.method == 'POST':
#             # Check if the form contains selected group IDs
#             if 'groups[]' in request.form:
#                 selected_groups = request.form.getlist('groups[]')
#                 # Do whatever processing you need to do with these group IDs
#             else:
#                 selected_groups = []  # If no groups are selected, set it to an empty list
#             # Render the home template and pass selected_groups as a variable
#             return render_template('home.html', selected_groups=selected_groups,usermailid=usermailid)
#         return render_template('home.html', usermailid=usermailid)
#     else:
#         return redirect(url_for('login'))
# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     selected_groups = None  # Initialize selected_groups variable
#     selected_recipients = None  # Initialize selected_groups variable
#     # usermailid = request.args.get('usermailid')
#     usermailid = session.get('usermailid')  
#     if request.method == 'POST':
#         # Check if the form contains selected group IDs
#         if 'groups[]' in request.form:
#             selected_groups = request.form.getlist('groups[]')
#             # Do whatever processing you need to do with these group IDs
#         else:
#             selected_groups = []  # If no groups are selected, set it to an empty list

#         if 'recipients[]' in request.form:
#             selected_recipients = request.form.getlist('recipients[]')
#             # Do whatever processing you need to do with these group IDs
#         else:
#             selected_recipients = []  # If no groups are selected, set it to an empty list
    
#     # Render the home template and pass selected_groups as a variable
#     return render_template('home.html', selected_groups=selected_groups,usermailid=usermailid, selected_recipients = selected_recipients)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Retrieve usermailid from session
    usermailid = session.get('usermailid')  

    # Initialize selected_groups and selected_recipients variables from session
    selected_groups = session.get('selected_groups', [])
    selected_recipients = session.get('selected_recipients', [])

    if request.method == 'POST':
        # Check if the form contains selected group IDs
        if 'groups[]' in request.form:
            # Get the selected groups from the form
            new_selected_groups = request.form.getlist('groups[]')
            # Append the newly selected groups to the existing list
            selected_groups += new_selected_groups

        # Check if the form contains selected recipient IDs
        if 'recipients[]' in request.form:
            # Get the selected recipients from the form
            new_selected_recipients = request.form.getlist('recipients[]')
            # Append the newly selected recipients to the existing list
            selected_recipients += new_selected_recipients

        # Remove duplicates from the lists
        selected_groups = list(set(selected_groups))
        selected_recipients = list(set(selected_recipients))

        # Update session variables with the updated lists
        session['selected_groups'] = selected_groups
        session['selected_recipients'] = selected_recipients
    else:
        # If it's a GET request, clear the session data for selected groups and recipients
        session.pop('selected_groups', None)
        session.pop('selected_recipients', None)
    # Render the home template and pass selected groups and recipients as variables
    return render_template('home.html', selected_groups=selected_groups, usermailid=usermailid, selected_recipients=selected_recipients)


@app.route('/seeRecipientList')
def RL():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Recipient_id, RecipientEmail_id, Recipient_name, Gender, Company, Age FROM RecipientList")
    recipients = cur.fetchall()
    cur.close()
    return render_template('seeRecipientList.html', recipients=recipients)

@app.route('/seeGroups')
# def seeGroups():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT Group_id, Group_name, Description, Criteria FROM Email_Group")
#     groups = cur.fetchall()
#     cur.close()
#     return render_template('seeGroups.html', groups=groups)
def groups():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Group_id, Group_name FROM Email_Group")
    groups = cur.fetchall()

    # Fetching group details might be more complex depending on your schema
    group_details = {}
    for group in groups:
        group_id = group[0]
        # Specify the table for ambiguous columns (e.g., RecipientList.Recipient_id)
        cur.execute("""
            SELECT RecipientList.Recipient_id, RecipientList.RecipientEmail_id, RecipientList.Recipient_name, RecipientList.Gender, RecipientList.Age 
            FROM RecipientList 
            JOIN Memberof ON RecipientList.Recipient_id = Memberof.Recipient_id 
            WHERE Memberof.Group_id = %s
        """, (group_id,))
        group_details[group_id] = cur.fetchall()


    return render_template('seeGroups.html', groups=groups, group_details=group_details)

@app.route('/delete-groups', methods=['POST'])
def delete_groups():
    data = request.get_json()
    group_ids = data['group_ids']
    group_ids = [int(id) for id in group_ids]

    placeholders = ','.join(['%s'] * len(group_ids))

    memberof_query = "DELETE FROM Memberof WHERE Group_id IN ({})".format(placeholders)

    email_group_query = "DELETE FROM Email_Group WHERE Group_id IN ({})".format(placeholders)

    cur = mysql.connection.cursor()
    cur.execute(memberof_query, group_ids)
    cur.execute(email_group_query, group_ids)
    
    mysql.connection.commit()  
    cur.close()

    return jsonify({'success': True})

# @app.route('/rename-group', methods=['POST'])
# def rename_group():
#     data = request.get_json()
#     group_id = data['group_id']
#     new_name = data['new_name']
#     # Add your logic to rename the group in the database


#     return jsonify({'success': True})

@app.route('/rename-group', methods=['POST'])
def rename_group():
    data = request.get_json()
    group_id = data['group_id']
    new_name = data['new_name']
    
    # Add your logic to rename the group in the database
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Email_Group SET Group_name = %s WHERE Group_id = %s", (new_name, group_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': True})



@app.route('/delete-recipients', methods=['POST'])
def delete_recipients():
    data = request.get_json()
    recipient_ids = data['recipient_ids']
    recipient_ids = [int(id) for id in recipient_ids]

    placeholders = ','.join(['%s'] * len(recipient_ids))

    memberof_query = "DELETE FROM Memberof WHERE Recipient_id IN ({})".format(placeholders)

    email_recipient_query = "DELETE FROM RecipientList WHERE Recipient_id IN ({})".format(placeholders)

    cur = mysql.connection.cursor()
    cur.execute(memberof_query, recipient_ids)
    cur.execute(email_recipient_query, recipient_ids)
    
    mysql.connection.commit()  
    cur.close()

    return jsonify({'success': True})


@app.route('/sentEmails')
def sent_emails():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch sent emails for the current user from the database
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM SentEmails WHERE User_id = %s", (user_id,))
    sent_emails = cur.fetchall()
    cur.close()
    return render_template('sentEmails.html', sent_emails=sent_emails)

@app.route('/chooseExistedGroups',methods=['GET', 'POST'])
def CEG():
    if request.method == 'POST':
        selected_groups = request.form.getlist('selected_groups')
        return render_template('home.html', selected_groups=selected_groups)
    cur = mysql.connection.cursor()
    cur.execute("SELECT Group_id, Group_name, group_address FROM Email_Group")
    groups = cur.fetchall()
    cur.close()
    return render_template('chooseExistedGroups.html', groups=groups)

@app.route('/chooseRecipientList', methods=['GET', 'POST'])
def CRL():
    # if request.method == 'POST':
    #     selected_recipients = request.form.getlist('selected_groups')
    #     return render_template('home.html', selected_groups=selected_groups)
    cur = mysql.connection.cursor()
    cur.execute("SELECT Recipient_id, Recipient_name, RecipientEmail_id FROM RecipientList")
    recipients = cur.fetchall()
    cur.close()
    return render_template('chooseRecipientList.html', recipients=recipients)


@app.route('/insertRecipient')
def insert_recipient_page():
    return render_template('insertRecipient.html')

@app.route('/insertRecipient', methods=['POST'])
def insert_recipient():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    recipient_email = request.form['recipient_email']
    recipient_name = request.form['recipient_name']
    gender = request.form['gender']
    company = request.form['company']
    age = request.form['age']

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO RecipientList (RecipientEmail_id, User_id, Recipient_name, Gender, Company, Age) VALUES (%s, %s, %s, %s, %s, %s)",
                    (recipient_email, session['user_id'], recipient_name, gender, company, age))
        mysql.connection.commit()
        return redirect(url_for('home'))
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()

# Route for deleting recipients
@app.route('/deleteRecipients', methods=['POST'])
def delete_r():
    try:
        # Get the list of recipient IDs to delete from the request data
        recipient_ids = request.json.get('recipientIds')

        if recipient_ids:
            # Connect to the database
            cur = mysql.connection.cursor()

            # Construct the SQL query to delete recipients based on their IDs
            query = "DELETE FROM RecipientList WHERE Recipient_id IN (%s)"
            query_params = ','.join(['%s'] * len(recipient_ids))
            query = query % query_params

            # Execute the SQL query
            cur.execute(query, tuple(recipient_ids))

            # Commit changes to the database
            mysql.connection.commit()

            # Close cursor and database connection
            cur.close()

            # Return success message
            return jsonify({'message': 'Recipients deleted successfully'}), 200
        else:
            # If no recipient IDs are provided in the request data
            return jsonify({'error': 'No recipient IDs provided in the request'}), 400

    except Exception as e:
        # If an error occurs during deletion
        return jsonify({'error': 'Error deleting recipients: {}'.format(str(e))}), 500

if __name__ == '__main__':
    app.run(debug=True)
