from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import requests
from pypdf import PdfReader

load_dotenv(override=True)

openai = OpenAI()

pushover_token = os.getenv("APP_KEY")
pushover_user = os.getenv("USER_KEY")
pushover_url = "https://api.pushover.net/1/messages.json"

if not pushover_token or not pushover_user:
    raise ValueError("Pushover token and user must be set in environment variables.")


user_session = {}

def push_notification(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)


# A function to allow users to get in touch with me
def record_user_detail(email, name="Name not provided", notes="notes not provided"):
    push_notification(f"New user: {name}\nEmail: {email}\nNotes: {notes}")
    return {"recorded": "ok"}

# A function to record a question provided by the user
def record_unknown_question(question):
    push_notification(f"New question: { question } asked that I couldn't answer.")
    return {"recorded": "ok"} 

def remember_user_details(email, name=None, notes=None):
    if email not in user_session:
        user_session[email] = {"name": name, "notes": notes}
    else:
        if name:
            user_session[email]["name"] = name
        if notes:
            user_session[email]["notes"] = notes
    return {"status": "User details updated", "email": email, "name": user_session[email]["name"], "notes": user_session[email]["notes"]}


# Tools
record_user_detail_tool = {
    "name": "record_user_detail",
    "description": "Use this tool to record user details for follow-up.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The user's email address."
            },
            "name": {
                "type": "string",
                "description": "The user's name."
            },
            "notes": {
                "type": "string",
                "description": "Additional notes about the user."
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_tool = {
    "name": "record_unknown_question",
    "description": "Use this tool to record a question that was not understood or couldn't be answered.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that was not understood."
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

remember_user_details_tool = {
    "name": "remember_user_details",
    "description": "Use this tool to remember user details for future interactions.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The user's email address."
            },
            "name": {
                "type": "string",
                "description": "The user's name."
            },
            "notes": {
                "type": "string",
                "description": "Additional notes about the user."
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}


tools = [{"type": "function", "function": record_user_detail_tool},{"type": "function", "function": record_unknown_question_tool}, {"type": "function", "function": remember_user_details_tool}]

def handle_tools(tools):
    if not tools:
        return None
    
    results = []
    for tool in tools:
        if tool.type == "function":
            tool_name = tool.function.name
            tool_args = json.loads(tool.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            
            if tool_name == "record_user_detail":
                result = record_user_detail(**tool_args)
            elif tool_name == "record_unknown_question":
                result = record_unknown_question(**tool_args)
            elif tool_name == "remember_user_details":
                result = remember_user_details(**tool_args)
            if result:
                results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool.id})
    return results


reader = PdfReader("me/profile.pdf")
linkedin_profile = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin_profile += text

with open("me/about.txt", "r", encoding="utf-8") as f:
    about_me = f.read()
    
name = "Josh Capito"

system_prompt = f"""You are acting as {name}. You are answering questions on {name}'s website, particularly questions related to {name}'s career, background, skills and experience.
Your responsibility is to represent {name} for interactions on the website as faithfully as possible.
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions.
Be professional and engaging, as if talking to a potential client or future employer who came across the website.
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career.
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_detail tool. If the user provides their name, email, or notes at any time, immediately call the remember_user_details tool to store this information. 
If you already know the user's email or details from earlier in the session, do not ask again. Use the remember_user_detail tool to store and recall user details during the session."""

system_prompt += f"\n\nHere is {name}'s LinkedIn profile:\n{linkedin_profile}\n\n"
system_prompt += f"Here is extra information about {name}:\n{about_me}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

def chat_with_user(message, history):
    user_details = ""
    if user_session:
        for email, details in user_session.items():
            user_details += f"Email: {email}, Name: {details.get('name', 'N/A')}, Notes: {details.get('notes', 'N/A')}\n"
    full_system_prompt = system_prompt
    full_system_prompt += f"\n\nUser details:\n{user_details}\n\n"
    messages = [{"role": "system", "content": full_system_prompt}] + history + [{"role": "user", "content": message}]
    done = False
    while not done:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            
            finish_reason = response.choices[0].finish_reason
            print(f"Finish reason: {finish_reason}", flush=True)
            
            # Allow the LLM to call the tools if needed
            if finish_reason == 'tool_calls':
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = handle_tools(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
                message = response.choices[0].message
                messages.append(message)
    return response.choices[0].message.content