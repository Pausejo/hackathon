import datetime
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from llama_index.llms.mistralai import MistralAI
from llama_index.core.llms import ChatMessage
import uvicorn
from supabase import create_client
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI()

rules = [
    {"horario de apertura": "Horario de apertura es de 10:00 a 18:00"},
    {"business_hours": "We are open Monday to Friday from 10:00 AM to 6:00 PM, Saturdays from 10:00 AM to 2:00 PM. Closed on Sundays."},
    {"payment_methods": "We accept cash, all major credit cards (Visa, Mastercard, American Express), and digital payments (Apple Pay, Google Pay)."},
    {"returns_policy": "Products can be returned within 30 days of purchase with original receipt. Items must be unused and in original packaging."},
    {"contact_info": "You can reach us at support@business.com, phone: (555) 123-4567, or visit us at 123 Business Street, City, State."},
    {"shipping": "Standard shipping takes 3-5 business days. Express shipping (1-2 days) is available for an additional fee. Free shipping on orders over $50."},
    {"appointments": "Appointments can be scheduled online through our website or by phone. Please give 24-hour notice for cancellations."},
    {"warranties": "All products come with a standard 1-year manufacturer warranty. Extended warranties are available for purchase."},
    {"discounts": "We offer 10% senior discount on Tuesdays, student discount with valid ID, and military discount. Sign up for our newsletter for exclusive deals."},
    {"parking": "Free parking available for customers in the lot behind our building. Street parking also available."},
    {"covid_policy": "We follow current health guidelines. Masks are optional. Hand sanitizer stations are available throughout the store."}
]

db = {
    "whatsapp:+34652341859": {
        "name": "Juan Perez",
        "language": "es",
        "customer_type": "premium"
    }
}


store = []

class ChatBot:
    def __init__(self):
        self.llm = MistralAI(api_key="")

    def chat(self, user_message, data_api):
        messages = [
            ChatMessage(role="system", content="You are a customer support assistant. You must answer in the same language as the user asks."),
            ChatMessage(role="system", content=f"You must follow these rules: {rules}. Current time is {datetime.datetime.now()}"),
            ChatMessage(role="system", content=f"Conversation history is a list where last items have more relevance: {store}"),
            ChatMessage(role="system", content=f"Answer personalized for the user. User data: {data_api}"),
            ChatMessage(role="user", content=user_message),
        ]
        resp = str(self.llm.chat(messages)).replace("assistant: ", "")

        print(resp)

        return resp   


chatbot = ChatBot()

@app.post("/api/whatsapp")
async def whatsapp_webhook(request: Request):
    # Parse the incoming WhatsApp message from Twilio
    form_data = await request.form()
    message_body = form_data.get("Body", "")

    store.append({"user": message_body, "timestamp": datetime.datetime.now()})

    from_number = form_data.get("From")
    print(from_number)
    data_api = db.get(from_number)
    print(data_api)

    # Get response from chatbot
    print(message_body)
    response = chatbot.chat(message_body, data_api=data_api)


    # Return TwiML response
    twiml = MessagingResponse()
    twiml.message(str(response))
    
    return Response(
        content=str(twiml),
        media_type="application/xml"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
