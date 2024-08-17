import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Your email credentials
your_email = "*******@gmail.com"
your_password = "******"

# GoDaddy SMTP server configuration
smtp_server = "smtpout.asia.secureserver.net"
smtp_port = 465  # SSL port

# Load the email list from an XLSX file
email_list = pd.read_excel("mailId.xlsx")

# Set up the server using SSL
server = smtplib.SMTP_SSL(smtp_server, smtp_port)
server.login(your_email, your_password)

# Loop through the email list and send emails
for index, row in email_list.iterrows():
    # Create the message
    msg = MIMEMultipart()
    msg['From'] = your_email
    msg['To'] = row['Email']
    msg['Subject'] = "Your Subject Here"

    # Email body
    body = f"Dear {row['Name']},\n\nThis is a bulk email sent via Python."
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    server.sendmail(your_email, row['Email'], msg.as_string())

# Close the server
server.quit()

print("Bulk email sent successfully.")
