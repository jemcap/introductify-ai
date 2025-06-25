# Introductify AI

**Introductify AI** is an agentic, OpenAI-powered conversational assistant designed to represent an individual on their website. It can answer questions about the person's background, career, and skills, and can record user details and questions for follow-up. The system integrates with Pushover for notifications and supports persistent user session memory during a conversation.

---

## Features

- **Conversational AI**: Uses OpenAI's GPT-4o to answer questions about the represented individual.
- **Session Memory**: Remembers user details (name, email, notes) during a session, reducing repeated prompts.
- **Tool Use**: Automatically records user details and unknown questions using function-calling tools.
- **Notifications**: Sends push notifications via Pushover when new user details or questions are recorded.
- **PDF & Text Ingestion**: Reads background/profile information from PDF and text files.
- **CORS-Enabled API**: FastAPI backend with CORS support for easy frontend integration.
- **Frontend-Ready**: Designed for easy integration with React or other frontend frameworks.

---

## Project Structure

```
introductify-ai/
├── agent.py         # Core agent logic, tools, and OpenAI integration
├── main.py          # FastAPI app exposing the chat API
├── me/
│   ├── profile.pdf  # PDF containing LinkedIn profile or resume
│   └── about.txt    # Additional background information
├── .env             # Environment variables (API keys, etc.)
└── requirements.txt # Python dependencies
```

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/introductify-ai.git
cd introductify-ai
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare Environment Variables

Create a `.env` file in the project root with the following:

```
OPENAI_API_KEY=your-openai-key
APP_KEY=your-pushover-app-key
USER_KEY=your-pushover-user-key
```

### 5. Add Profile Information

- Place your LinkedIn/resume PDF in `me/profile.pdf`
- Place extra info in `me/about.txt`

---

## Running the API

```bash
uvicorn main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## API Usage

### Health Check

```http
GET /
```

### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "message": "Hello, I'm interested in working with you.",
  "history": [
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello! How can I help you?"}
  ]
}
```

**Response:**
```json
{
  "response": "Thank you for your interest! Could you please share your email so I can follow up?"
}
```

- **message**: The user's current message.
- **history**: (Required) The full conversation history as a list of `{role, content}` objects. This is necessary for the agent to maintain context and memory.

---

## Frontend Integration

When integrating with a frontend (e.g., React), always send the full conversation history with each request. Example:

```js
const response = await axios.post("http://127.0.0.1:8000/chat", {
  message: input,
  history: messages.map(msg => ({ role: msg.role, content: msg.text }))
});
```

---

## Customisation

- **Change the Represented Person**: Update the `name` variable and replace `me/profile.pdf` and `me/about.txt`.
- **Modify System Prompt**: Edit the `system_prompt` in `agent.py` to adjust the assistant's persona or behavior.
- **Add More Tools**: Extend the tools section in `agent.py` for additional agent capabilities.

---

## Security & Privacy

- User details and questions are stored in memory for the session and are not persisted long-term.
- Pushover notifications are sent for new user details and unknown questions.
- For production, consider adding persistent storage and authentication.

---

## License

MIT License

---

## Acknowledgments

- [OpenAI](https://openai.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pushover](https://pushover.net/)
- [PyPDF](https://pypdf.readthedocs.io/)

---

## Contact

For questions or collaboration, please reach out via the contact details provided in your `about.txt` or LinkedIn profile.
