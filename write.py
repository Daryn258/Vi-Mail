import speech_recognition as sr
import pyttsx3
from email.message import EmailMessage
import tkinter as tk
from tkinter import scrolledtext
import ssl
import smtplib
import openai


openai.api_key = 'your api key'

def generate_automatic_response(input_message):
    engine = pyttsx3.init()
    prompt = "User: " + input_message + "\nAI:"
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=500
    )
    print("Generated email: "+response.choices[0].text.strip())
    engine.say(response.choices[0].text.strip())
    return response.choices[0].text.strip()

  
    return response.choices[0].text.strip()
def get_voice_input_email():

    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    
    with sr.Microphone() as source:
        msg="Listening..."
        engine.say("Listening...")
        # console.insert(tk.END, msg + '\n')
        # console.update_idletasks()
        engine.runAndWait()
        
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        msg="Recognizing email address..."
        engine.say("Recognizing email address...")
        # console.insert(tk.END, msg + '\n')
        # console.update_idletasks()
        engine.runAndWait()
        
        text = recognizer.recognize_google(audio)

        cleaned_email = text.replace(" ", "").lower()
        cleaned_email += "@gmail.com"

        # print(cleaned_email)
        # print("You said: " + cleaned_email)
        msg=f"You said : {cleaned_email}"
        engine.say("You said: " + cleaned_email)
        # console.insert(tk.END, msg + '\n')
        # console.update_idletasks()
        engine.runAndWait()
        print(cleaned_email)
        
        return cleaned_email
    
def get_voice_input():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    
    with sr.Microphone() as source:
        print("Listening...")
        engine.say("Listening...")
        engine.runAndWait()
        
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
    try:
        print("Recognizing...")
        engine.say("Recognizing...")
        engine.runAndWait()
        
        text = recognizer.recognize_google(audio)
        print("You said: " + text.capitalize())
        engine.say("You said: " + text)
        engine.runAndWait()
        
        return text
    except sr.UnknownValueError:
        engine.say("Sorry, I could not understand your voice.")
        engine.runAndWait()
        return ""
    except sr.RequestError as e:
        engine.say("Could not request results from Google Speech Recognition service.")
        engine.runAndWait()
        return ""

def send_email(email_sender, email_password, email_receiver, subject, body):
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

email_sender = 'your email here'
email_password = 'your password here'
