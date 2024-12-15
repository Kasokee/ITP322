from flask import Flask, request, render_template, flash, redirect, url_for
from datetime import datetime, timedelta
import threading
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint

app = Flask(__name__)
app.secret_key = '\xbd\x14\x1eL!\x0f\x93\xf1\xe5\xdf#\x0c\x9bH\xec3\xad\x94(\x8e\xb4\xcf\x8e' 

# ==== MY BREVO API KEY ====
BREVO_API_KEY = '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'

# ==== CONFIG FOR BREVO API ====
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY

reminders = []

def sendEmail(email, reminder_name, personal_name, reminder_datetime, message):
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    userEmail = {
        "to": [{"email": email}],
        "sender": {"name": "Task/Event Reminder", "email": "frijholytz08@gmail.com"},
        "subject": f"Reminder: {reminder_name}",
        "html_content": f"""
            <h1>Reminder Name: {reminder_name}</h1>
            <strong><p>NAME: {personal_name}</p></strong>
            <strong><p>DATE & TIME: {reminder_datetime.strftime('%Y-%m-%d %H:%M')}</p></strong>
            <strong><p>MESSAGE: {message}</p></strong>
            <br>
            <p>Dear {personal_name}, your reminder has ended. Thank you for using our Website. If you want to create a new reminder, just click the button below.</p>
            <a href="/">Set Another Reminder</a>
            <br>
            <strong>Best Regards,</strong>
            <p>Justine Andrei A. Tacorda</p>
            <p>Nadine Rojas</p>
            <p>Lenard Gil Llorca</p>
        """
    }

    try:
        response = api_instance.send_transac_email(sib_api_v3_sdk.SendSmtpEmail(**userEmail))
        print("Email sent successfully!")
        pprint(response)
        return True
    except ApiException as e:
        print("Exception when sending email:")
        print(f"Status Code: {e.status}")
        print(f"Reason: {e.reason}")
        print(f"Body: {e.body}")
        return False

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/setReminder', methods=['GET', 'POST'])
def setReminder():
    if request.method == 'POST':
        reminder_name = request.form['reminderName']
        personal_name = request.form['personalName']
        email = request.form['email']
        date = request.form['date']
        time = request.form['time']
        message = request.form.get('message', 'No message provided.')

        reminder_datetime = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
        reminders.append({
            'reminder_name': reminder_name,
            'personal_name': personal_name,
            'email': email,
            'reminder_datetime': reminder_datetime,
            'message': message
        })

        flash("You have set your reminder and will receive an email at the specified time!", "success")

        return redirect(url_for('confirmation', reminderName=reminder_name, personalName=personal_name, email=email, date=date, time=time, message=message))

    return render_template('index.html')

@app.route('/confirmation')
def confirmation():
    reminder_name = request.args.get('reminderName')
    personal_name = request.args.get('personalName')
    email = request.args.get('email')
    date = request.args.get('date')
    time = request.args.get('time')
    message = request.args.get('message')

    return render_template('confirmation.html', reminderName=reminder_name, personalName=personal_name, email=email, date=date, time=time, message=message)

def check_reminders():
    while True:
        now = datetime.now()
        for reminder in reminders[:]:
            if now >= reminder['reminder_datetime']:
                sendEmail(reminder['email'], reminder['reminder_name'], reminder['personal_name'], reminder['reminder_datetime'], reminder['message'])
                reminders.remove(reminder)
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=check_reminders, daemon=True).start()
    app.run(debug=True)
