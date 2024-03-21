import smtplib
from email.message import EmailMessage

acceptance_template = """\
Hi {name},

This email confirms that WJTB can provide live sound for your event, {event_name}, on {date}.

Best,
The WJTB Team
"""

rejection_template = """\
Hi {name},

Thank you for submitting a live sound request for WJTB! Unfortunately we cannot do your event, {event_name}, on {date} due to {reason}.

Our apologies, 
The WJTB Team
"""

def send_live_events_email(name, email, event_name, accepted, reason):
	live_events_email = None
	with open("live_events_email.secret", "r") as f:
		live_events_email = f.read()
	if(live_events_email is None):
		return "Config error: no live events email"
	live_events_password = None
	with open("live_events_password.secret", "r") as f:
		live_events_password = f.read()
	if(live_events_password is None):
		return "Config error: no live events password"

	msg = EmailMessage()

	accepted = False
	filled_template = acceptance_template if accepted else rejection_template
	filled_template = filled_template.format(name=name, event_name=event_name, date=date.strftime('%A, %B %d, %Y'), reason=reason)
	msg.set_content(filled_template)

	msg['Subject'] = f'WJTB Sound Request'
	msg['From'] = "wjtb@njit.edu"
	msg['To'] = email

	s = smtplib.SMTP('smtp.gmail.com', port=587)
	s.starttls()
	s.login(live_events_email, live_events_password)

	s.send_message(msg)
	s.quit()

	return filled_template
