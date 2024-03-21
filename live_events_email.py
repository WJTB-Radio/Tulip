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
	s.login(os.environ["TULIP_LIVE_EVENTS_EMAIL"], os.environ["TULIP_LIVE_EVENTS_PASSWORD"])

	s.send_message(msg)
	s.quit()

	return filled_template
