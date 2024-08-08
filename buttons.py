import openai
import speech_recognition as sr
import tkinter as tk
import smtplib
import calendar
import datetime as dt
from tkinter import scrolledtext
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import messagebox
from email.header import decode_header
from read import read_emails
import write
import read
import email
import pyttsx3
import imaplib
import threading
openai.api_key = 'your api key'
engine = pyttsx3.init()

marked_emails = []
markedemail = []

def read_emails_button():

    def decode_email_header(header):
        decoded_header = decode_header(header)
        decoded_text = ""
        for part, encoding in decoded_header:
            if isinstance(part, bytes):
                decoded_text += part.decode(encoding or 'utf-8')
            else:
                decoded_text += part
        return decoded_text

    def generate_automatic_response(input_message):
        engine = pyttsx3.init()
        prompt = "User: " + input_message + "\nAI:"

        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=500
        )
        msg= "Generated response: " + response.choices[0].text.strip()
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.say(response.choices[0].text.strip())
        return response.choices[0].text.strip()

    def translate_to_english(translate):
        prompt = "User: " + translate + "\n\nDetect the language of the above message and translate it into English. If it is already in English,then just return 'This message is already in English'. If not, then return your answer in this format\nDetected Language: \nTranslation: " + "\nAI:"

        translation = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=200
        )

        return translation.choices[0].text.strip()

    def send_email(subject, message, to_email, from_email, password):
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()

    def listen_for_reply():
        recognizer = sr.Recognizer()
        engine = pyttsx3.init()

        with sr.Microphone() as source:
            msg="Listening..."
            engine.say("Listening...")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()

            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source,timeout=5)

        try:
            msg="Recognizing..."
            engine.say("Recognizing...")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()

            text = recognizer.recognize_google(audio)
            msg="You said: " + text.capitalize()
            engine.say("You said: " + text)
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()

            return text
        except sr.UnknownValueError:
            msg="Sorry, I could not understand your voice."
            engine.say("Sorry, I could not understand your voice.")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()
            return ""
        except sr.RequestError as e:
            msg="Could not request results from Google Speech Recognition Service"
            engine.say("Could not request results from Google Speech Recognition service.")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()
            return ""

    def read_emails():
        imap_server = 'imap.gmail.com'
        imap_port = 993
        imap_username = 'your email here'
        imap_password = 'your password here'

        smtp_username = 'your email here''
        smtp_password = 'your password here'

        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(imap_username, imap_password)

        mailbox = 'INBOX'
        imap.select(mailbox)



        search = 'UNSEEN'
        _, msgnums = imap.search(None, search)
        msgnums = msgnums[0].split()[::-1]

        # marked_emails = []
        if not msgnums:
            engine.say("You have no unread emails.")
            console.insert(tk.END, "You have no unread emails.\n")
            console.update_idletasks()
            engine.runAndWait()
        for msgnum in msgnums:
            _, data = imap.fetch(msgnum, "(RFC822)")

            message = email.message_from_bytes(data[0][1])

            sender_name_full = decode_email_header(message.get('From')).split('<')[0].strip()
            sender_first_name = sender_name_full.split()[0]
            recipient_name = decode_email_header(message.get('To')).split('<')[0].strip()

            msg=f"{sender_first_name} sent you an email with subject as {message.get('Subject')}"
            engine.say(f"{sender_first_name} sent you an email with subject as {message.get('Subject')}")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()

            engine.say("Content: ")
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    content = part.get_payload(decode=True).decode()
                    msg=f"Content : {content}"
                    engine.say(content)
                    console.insert(tk.END, msg + '\n')
                    console.update_idletasks()
                    engine.runAndWait()
                    
                    msg="Do you want to translate this into English?"
                    engine.say("Do you want to translate this into English?")
                    console.insert(tk.END, msg + '\n')
                    console.update_idletasks()
                    engine.runAndWait()
                    reply_translate = listen_for_reply()
                    if"yes" in reply_translate:
                        translated_content = translate_to_english(content)
                        engine.say(translated_content)
                        msg = translated_content
                        console.insert(tk.END, msg + '\n')
                        console.update_idletasks()
                        engine.runAndWait()
                        # engine.say(content[0:30])
                    else:
                        break
            
            msg="Do you want to mark this email as important?"
            engine.say("Do you want to mark this email as important?")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()
            reply = listen_for_reply()

            if "yes" in reply:
                content1 = part.get_payload(decode=True).decode()
                # Perform marking as important logic here
                msg="Email marked as important."
                engine.say("Email marked as important.")
                console.insert(tk.END, msg + '\n')
                console.update_idletasks()
                engine.runAndWait()
                marked_emails.append((sender_first_name, message.get('Subject'),content1))
                markedemail.append((sender_first_name, message.get('Subject'),content1))
            msg="Do you want to reply to this email?"
            engine.say("Do you want to reply to this email?")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()
            reply = listen_for_reply()

            if "yes" in reply:
                msg="Do you want a generated reply?"
                engine.say("Do you want a generated reply?")
                console.insert(tk.END, msg + '\n')
                console.update_idletasks()
                engine.runAndWait()
                reply1 = listen_for_reply()
                if "yes" in reply1:

                    automatic_response = generate_automatic_response(content)
                    msg = "Are you satisfied with this as your reply?"
                    engine.say("Are you satisfied with this as your reply?")
                    console.insert(tk.END, msg + '\n')
                    console.update_idletasks()
                    engine.runAndWait()
                    reply = listen_for_reply()
                    if "yes" in reply:
                        send_email("Re: " + message.get('Subject'), automatic_response, message.get('From'),
                                   smtp_username,
                                   smtp_password)
                        msg = "Automatic response sent successfully!"
                        engine.say("Automatic response sent successfully")
                        console.insert(tk.END, msg + '\n')
                        console.update_idletasks()
                        engine.runAndWait()
                    else:
                        def generated_change():
                            msg = "Please mention the changes required"
                            engine.say("Please mention the changes required")
                            console.insert(tk.END, msg + '\n')
                            console.update_idletasks()
                            engine.runAndWait()
                            content1 = listen_for_reply()
                            final_content= automatic_response +"/n/n"+ content1
                            final_response = generate_automatic_response(final_content)
                            engine.runAndWait()
                            msg = "Are you satisfied with this as your reply?"
                            engine.say("Are you satisfied with this as your reply?")
                            console.insert(tk.END, msg + '\n')
                            console.update_idletasks()
                            engine.runAndWait()
                            reply = listen_for_reply()
                            if "yes" in reply:
                                send_email("Re: " + message.get('Subject'), final_response, message.get('From'),
                                           smtp_username,
                                           smtp_password)
                                msg = "Automatic response sent successfully!"
                                engine.say("Automatic response sent successfully")
                                console.insert(tk.END, msg + '\n')
                                console.update_idletasks()
                                engine.runAndWait()
                            else:
                                generated_change()
                        generated_change()

                else:
                    def dictate_reply():
                        msg="Please dictate your reply"
                        engine.say("Please dictate your reply.")
                        console.insert(tk.END, msg + '\n')
                        console.update_idletasks()
                        engine.runAndWait()
                        reply_message = listen_for_reply()
                        msg = "Is this message correct?"
                        engine.say("Is this message correct?")
                        console.insert(tk.END, msg + '\n')
                        console.update_idletasks()
                        engine.runAndWait()
                        reply = listen_for_reply()
                        if "yes" in reply:
                            send_email("Re: " + message.get('Subject'), reply_message.capitalize(), message.get('From'),
                                       smtp_username,
                                       smtp_password)
                            msg = "Response sent successfully!"
                            engine.say("Response sent successfully!")
                            console.insert(tk.END, msg + '\n')
                            console.update_idletasks()
                            engine.runAndWait()
                        else:
                            dictate_reply()
                    dictate_reply()

            else:
                msg="Moving to next email..."
                console.insert(tk.END, msg + '\n')
                console.update_idletasks()

            msg="Do you want to continue hearing further emails?"
            engine.say("Do you want to continue hearing further emails?")
            console.insert(tk.END, msg + '\n')
            console.update_idletasks()
            engine.runAndWait()

            continue_hearing = listen_for_reply()

            if "yes" in continue_hearing:
                read_emails()

            else:
                msg="Exiting"
                engine.say("Exiting")
                console.insert(tk.END, msg + '\n')
                console.update_idletasks()
                break
        engine.runAndWait()
        imap.close()
    read_emails()


def generate_automatic_response(input_message):
    engine = pyttsx3.init()
    prompt = "User: " + input_message + "\nAI:"
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=500
    )
    msg="Generated email: "+response.choices[0].text.strip()
    engine.say(response.choices[0].text.strip())
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    return response.choices[0].text.strip()


def get_voice_input():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()

    with sr.Microphone() as source:
        msg="Listening..."
        engine.say("Listening...")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source,timeout=5)

    try:
        msg="Recognizing..."
        engine.say("Recognizing...")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

        text = recognizer.recognize_google(audio)
        msg="You said: " + text.capitalize()
        engine.say("You said: " + text)
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

        return text
    except sr.UnknownValueError:
        msg="Sorry, I could not understand your voice"
        engine.say("Sorry, I could not understand your voice.")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()
        return ""
    except sr.RequestError as e:
        msg="Could not request results from Google Speech Recognition service"
        engine.say("Could not request results from Google Speech Recognition service.")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()
        return ""


def get_voice_input_email():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()

    with sr.Microphone() as source:
        msg = "Listening..."
        engine.say("Listening...")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source,timeout=5)
        msg = "Recognizing email address..."
        engine.say("Recognizing email address...")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

        text = recognizer.recognize_google(audio)

        cleaned_email = text.replace(" ", "").lower()
        cleaned_email += "@gmail.com"

        # print(cleaned_email)
        # print("You said: " + cleaned_email)
        msg = f"You said : {cleaned_email}"
        engine.say("You said: " + cleaned_email)
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()
        msg=(cleaned_email)
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()

        return cleaned_email


def write_email_button():

    msg = 'Please speak the email address of the recipient: '
    engine.say("Please speak the email address of the recipient.")
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    email_recipient = get_voice_input_email()
    # email_recipient = input("email")
    console.insert(tk.END, 'Email ID: ' + str(email_recipient) + '\n')
    console.update_idletasks()

    msg = 'Please speak the subject of the email: '
    engine.say("Please speak the subject of the email.")
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    subject = get_voice_input()
    # subject = input("subject")

    console.insert(tk.END, str(subject.capitalize()) + '\n')
    console.update_idletasks()

    msg = 'Do you want to generate an email? : '
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.say("Do you want to generate an email?")
    engine.runAndWait()
    new_input = get_voice_input()
    # new_input = input("say generate")
    console.insert(tk.END, str(new_input)+ '\n')

    if "yes" in new_input:
        msg = 'Tell me what you want to write about: '
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.say("Tell me what you want to write about")
        # new_input = input("say generate")
        input_message = get_voice_input()
        console.insert(tk.END, 'Your Prompt was: '+ str(input_message) + '\n')
        body = generate_automatic_response(input_message)
        console.insert(tk.END, 'Body of Email: ' + str(body) + '\n')
        console.update_idletasks()
        msg = "Are you satisfied with this as your reply?"
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.say("Are you satisfied with this as your reply?")
        engine.runAndWait()
        reply = get_voice_input()
        if "yes" in reply:
            if email_recipient and subject:
                write.send_email(write.email_sender, write.email_password, email_recipient, subject, body)

        else:
            def generated_change():
                msg = "Please mention the changes required"
                engine.say("Please mention the changes required")
                console.insert(tk.END, msg + '\n')
                console.update_idletasks()
                engine.runAndWait()
                content1 = get_voice_input()
                final_content = body + "\n\n" + content1
                console.insert(tk.END, 'Your Prompt was: '+ str(content1) + '\n')
                console.update_idletasks()
                automatic_response = generate_automatic_response(final_content)
                msg = "Are you satisfied with this as your reply?"
                engine.say("Are you satisfied with this as your reply?")
                console.insert(tk.END, msg + '\n')
                console.update_idletasks()
                engine.runAndWait()
                reply = get_voice_input()
                if "yes" in reply:
                    if email_recipient and subject:
                        write.send_email(write.email_sender, write.email_password, email_recipient, subject, automatic_response)
                else:
                    generated_change()

            generated_change()
        msg="Email sent successfully"
        engine.say("Email sent successfully!")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

    elif "no" in new_input:
        msg="Please speak the body of the email"
        engine.say("Please speak the body of the email.")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()
        body = get_voice_input()
        msg=f"Body : {body}"
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        msg="Email sent successfully"
        engine.say("Email sent successfully")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

    else:
        msg="I didnt get that"
        engine.say("I didnt get that")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()
        write_email_button()

    if email_recipient and subject:
        write.send_email(write.email_sender, write.email_password, email_recipient, subject, body)


# Function to handle the "Schedule Email" button click
def schedule_email_from_voice(callback=None):
    def schedule_email(recipient_email, body):
        engine = pyttsx3.init()
        email_user = 'your email here'
        email_password = 'your password here'
        email_recipient = recipient_email

        message = MIMEMultipart()
        message['From'] = email_user
        message['To'] = email_recipient
        message['Subject'] = 'Scheduled Email'

        message.attach(MIMEText(body.capitalize(), 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.sendmail(email_user, email_recipient, message.as_string())

        engine.say("Email sent successfully")
        engine.runAndWait()
        msg="Email sent successfully!"
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()

    def parse_month(month_name):
        return list(calendar.month_name).index(month_name.capitalize())

    engine = pyttsx3.init()

    msg="Please say the date in 'day month year' format:"
    engine.say("Please say the date in 'day month year' format:")
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    date_input = get_voice_input()
    msg="Recognized Date:"+str(date_input)
    console.insert(tk.END, msg)
    console.insert(tk.END, '\n')
    console.update_idletasks()
    msg="Please say the time in 'hour minute' format (24-hour):"
    engine.say("Please say the time in 'hour minute' format (24-hour):")
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    time_input = get_voice_input()
    # time_input= input("Time")
    msg="Recognized Time:" +str(time_input)
    console.insert(tk.END, msg)
    console.insert(tk.END,'\n')
    console.update_idletasks()
    msg="Please say the recipient's email address:"
    engine.say("Please say the recipient's email address:")
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    recipient_email = get_voice_input()
    # recipient_email = input("email")
    recipient_email = recipient_email.replace(" ", "").lower()
    recipient_email += "@gmail.com"
    msg="Recipient's Email:" +str(recipient_email)
    console.insert(tk.END, msg)
    console.insert(tk.END, '\n')
    console.update_idletasks()
    msg="Please dictate the email body:"
    engine.say("Please dictate the email body:")
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()
    engine.runAndWait()
    body = get_voice_input()
    msg="Body:" +str(body.capitalize())
    engine.say("Email scheduled successfully!")
    console.insert(tk.END, msg)
    console.insert(tk.END, '\n')
    console.update_idletasks()
    engine.runAndWait()
    msg="Email scheduled successfully!"
    console.insert(tk.END, msg + '\n')
    console.update_idletasks()

    day, month_name, year = date_input.split()
    month = parse_month(month_name)
    hour, minute = map(int, [time_input[:2], time_input[2:]])
    # hour, minute = map(int, time_input.split(":"))
    # hour = map(int,time_input[:2])
    # minute = map(int,time_input[2:])

    scheduled_time = dt.datetime(int(year), month, int(day), hour, minute)
    current_time = dt.datetime.now()
    delay = (scheduled_time - current_time).total_seconds()

    if delay > 0:
        threading.Timer(delay, schedule_email, args=[recipient_email, body]).start()
    else:
        msg="The scheduled time has already passed."
        engine.say("The scheduled time has already passed!")
        console.insert(tk.END, msg + '\n')
        console.update_idletasks()
        engine.runAndWait()

    if callback:
        callback()


# Function to handle the "Read Marked Emails" button click
def read_marked_emails_button():
        console.insert(tk.END, "READING MARKED EMAILS: " + '\n')
        console.update_idletasks()
        print(markedemail)
        #marked_email = marked_emails
        # messagebox.showinfo("Marked Emails", f"Marked Emails: {marked_emails}")
        #msg=f"Marked emails: "+str(marked_email)
        sender = markedemail[0][0]  # Extracts 'Ishaan'
        sub = markedemail[0][1]  # Extracts 'Hello'
        content = markedemail[0][2].strip()
        
        msg = f"{sender} sent you an email with subject as {sub}. Content: {content}"
        printmessage = f"Sender: {sender}\nSubject: {sub}\nContent: {content}"
        # engine.say(f"{sender_first_name} sent you an email with subject as {message.get('Subject')}")
        # console.insert(tk.END, msg + '\n')
        # console.update_idletasks()
        # engine.runAndWait()
        # print(marked_emails.strip())

        engine.say(msg)
        engine.runAndWait()
        console.insert(tk.END, printmessage + '\n')
        console.update_idletasks()
            
        

# Callback function for the scheduled email
def my_callback_function():
    messagebox.showinfo("Email Scheduled", "Email scheduled. Continuing with other tasks...")
# engine.say("Welcome to the email service. Please give a command.")
# Create the main application window
# Create the main Tkinter window
root = tk.Tk()
root.title("Vi.Mail")
root.configure(bg="black")

# Top padding frame
top_padding = tk.Frame(root, height=20, bg='black')
top_padding.pack(fill="x")

# Logo Label
label = tk.Label(root, text="Vi.Mail", font=("Helvetica", 36, "bold"), pady=20, bg='black', fg='white')
label.pack()

# Console Text
console_font = ("Helvetica", 14)
console = scrolledtext.ScrolledText(root, font=console_font, bg="white", fg="black", wrap=tk.WORD, width=60, height=20)
console.pack(pady=10, padx=20)

def scroll_to_bottom(*args):
    console.yview(tk.END)

console.config(yscrollcommand=scroll_to_bottom)

# Function to automatically scroll to the bottom when new text is inserted
def on_text_insert(index1, index2):
    console.yview_moveto(1.0)

# Bind the on_text_insert function to the <Key> event, which occurs when text is inserted
console.bind("<Key>", on_text_insert)

# Create a frame for left-side buttons
left_frame = tk.Frame(root, bg="black")
left_frame.pack(side=tk.LEFT, padx=20, pady=20)

# Create a frame for right-side buttons
right_frame = tk.Frame(root, bg="black")
right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

# Define the custom style for the buttons
button_style = {
    "bg": "#007BFF",  # Blue
    "fg": "white",
    "font": ("Helvetica", 14, "bold"),
    "width": 20,
    "height": 2,
    "relief": tk.RAISED,
    "bd": 3,  # Border width
}

# Create buttons for different functions with custom style
read_button = tk.Button(left_frame, text="Read Emails", command=read_emails_button, **button_style)
read_button.pack(pady=10)

write_button = tk.Button(left_frame, text="Write Email", command=write_email_button, **button_style)
write_button.pack(pady=10)

schedule_button = tk.Button(right_frame, text="Schedule Email", command=schedule_email_from_voice, **button_style)
schedule_button.pack(pady=10)

read_marked_button = tk.Button(right_frame, text="Read Marked Emails", command=read_marked_emails_button, **button_style)
read_marked_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()

