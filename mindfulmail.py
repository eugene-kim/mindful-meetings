####
# function: emailuser()
# mailto: Is the user's email address you want to send the warning
# mailtype: either 5, 10, or 15 minutes
#           Put in the number of minutes for no motion detected in room
#
# Example: emailuser("kyoung@kenzyworld.com", 5)
####
def emailuser(mailto, mailtype):
	# Import smtplib to provide email functions
	import smtplib
	  
	# Import the email modules
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	mailtype_s = str(mailtype)

	if (mailtype == 5) or (mailtype == 10):
		emailsubject = mailtype_s + " Minute Warning"
		text = "We have detected no activity in your meeting room.\nPlease release your room:"
		html = """\
		<html>
		  <head></head>
		  <body>
		    <p><b>We have detected no activity in your meeting room for """ + mailtype_s + """ minutes.</b></p>
		    <p>Please release your room if you not longer need the room:</p>
		    <p>---The Mindful Meeting Team</p>
		  </body>
		</html>
		"""

	elif (mailtype == 15):
		emailsubject = "Meeting Room Unbooked"
		text = "Sorry, we have detected no activity in your meeting room for 15 minutes.\nWe have unbooked your room."
		html = """\
		<html>
		  <head></head>
		  <body>
		    <p><b>Sorry, we have detected no activity in your meeting room for """ + mailtype_s + """ minutes.</b></p>
		    <p>We have unbooked your room.</p>
		    <p>---The Mindful Meeting Team</p>
		  </body>
		</html>
		"""

	else:
		print "ERROR: mailtype value should be either 5, 10 or 15"
		exit()

	# Define email addresses to use
	addr_to   = mailto
	addr_from = 'DO_NOT_REPLY@kenzyworld.com'
	  
	# Define SMTP email server details
	smtp_server = 'smtp.gmail.com'
	smtp_user   = 'mindful-meetings@kenzyworld.com'
	smtp_pass   = 'abc123456'
	  
	# Construct email
	msg = MIMEMultipart('alternative')
	msg['To'] = addr_to
	msg['From'] = addr_from
	msg['Subject'] = emailsubject
	  
	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')
	  
	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)
	  
	# Send the message via an SMTP server
	try:
	  s = smtplib.SMTP(smtp_server, 587)
	  s.ehlo()
	  s.starttls()
	  s.login(smtp_user,smtp_pass)
	  s.sendmail(addr_from, addr_to, msg.as_string())
	  s.quit()
	except:
	  print("There was an error sending the email. Check the smtp settings.")

