from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)

openai = OpenAI()

pushover_token = os.getenv("APP_KEY")
pushover_user = os.getenv("USER_KEY")
pushover_url = "https://api.pushover.net/1/messages.json"

if not pushover_token or not pushover_user:
    raise ValueError("Pushover token and user must be set in environment variables.")

def push_notification(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

push_notification("Testing")