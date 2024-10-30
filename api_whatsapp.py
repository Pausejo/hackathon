import datetime
import os
from fastapi import FastAPI, Request, Response
from twilio.rest import Client
from supabase import create_client, Client as SupabaseClient
import uvicorn
from twilio.twiml.messaging_response import MessagingResponse
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from dotenv import load_dotenv
load_dotenv()

from memory_graph import get_graph
app = FastAPI()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: SupabaseClient = create_client(supabase_url, supabase_key)

# Initialize Twilio client
twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_client = Client(twilio_account_sid, twilio_auth_token)


@app.post("/api/whatsapp")
async def receive_whatsapp(request: Request):
    print("===REQUEST WHATSAPP===")
    # Get the form data from the Twilio webhook
    form_data = await request.form()
    
    # Extract message details
    message_body = form_data.get("Body", "")
    from_number = form_data.get("From", "")
    message_sid = form_data.get("MessageSid", "")

    print("===msg=====")
    print(form_data)
    print(message_body)
    print(from_number)
    print(message_sid)
    print("========")
    
    try:
        # Check if a thread exists for this phone number
        result = supabase.table("threads").select("reference").eq("reference", from_number).execute()
        
        message_data = {
            "role": "user",
            "content": message_body,
            "message_sid": message_sid,
            "timestamp": datetime.datetime.now().isoformat()
        }

        if not result.data:
            # Create new thread if it doesn't exist
            thread_data = {
                "reference": from_number,
                "conversation_history": [message_data]
            }
            supabase.table("threads").insert(thread_data).execute()
        else:
            # Update existing thread with new message
            supabase.table("threads")\
                .update({"conversation_history": supabase.table("threads").select("conversation_history").single().execute().data["conversation_history"] + [message_data]})\
                .eq("reference", from_number)\
                .execute()
            
        # Generate response
        input_message = HumanMessage(content=message_body)
        config = {"configurable": {"thread_id": from_number}}
        output = get_graph().invoke({"messages": [input_message]}, config)
        for m in output['messages']:
            m.pretty_print()
        response = output['messages'][-1].content
        
        # Save response to thread conversation history
        response_data = {
            "role": "assistant", 
            "content": response,
            "message_sid": message_sid,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Get current conversation history
        thread = supabase.table("threads").select("conversation_history").eq("reference", from_number).execute()
        conversation_history = thread.data[0]["conversation_history"]
        
        # Append new response and update
        conversation_history.append(response_data)
        supabase.table("threads")\
            .update({"conversation_history": conversation_history})\
            .eq("reference", from_number)\
            .execute()
            
        # Return TwiML response
        twiml = MessagingResponse()
        twiml.message(str(response))
        
        return Response(
            content=str(twiml),
            media_type="application/xml"
        )
        
    except Exception as e:
        print("===ERROR===")
        print(e)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("api_whatsapp:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
