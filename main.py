import datetime
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from llama_index.llms.mistralai import MistralAI
from llama_index.core.llms import ChatMessage
import uvicorn
from supabase import create_client
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

class ChatBot:
    def __init__(self):
        self.llm = MistralAI(api_key="")

    def chat(self, user_message):
        messages = [
            ChatMessage(role="system", content="you are a customer support assistant"),
            ChatMessage(role="user", content=user_message),
        ]
        resp = self.llm.chat(messages) 

        return resp   


chatbot = ChatBot()

@app.post("/api/whatsapp")
async def whatsapp_webhook(request: Request):
    # Parse the incoming WhatsApp message from Twilio
    form_data = await request.form()
    message_body = form_data.get("Body", "")

    
    # Get response from chatbot
    app.logger.info(message_body)
    response = chatbot.chat(message_body)


    # Return TwiML response
    twiml = MessagingResponse()
    twiml.message(str(response))
    
    return Response(
        content=str(twiml),
        media_type="application/xml"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
