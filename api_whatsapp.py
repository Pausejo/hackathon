import os
from fastapi import FastAPI, Request
from twilio.rest import Client
from supabase import create_client, Client as SupabaseClient
import uvicorn
from dotenv import load_dotenv
load_dotenv()

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
    timestamp = form_data.get("MessageSid", "")

    print("===msg=====")
    print(form_data)
    print(message_body)
    print(from_number)
    print(timestamp)
    print("========")
    
    try:
        # Check if a thread exists for this phone number
        result = supabase.table("threads").select("reference").eq("reference", from_number).execute()
        
        message_data = {
            "role": "user",
            "content": message_body,
            "timestamp": timestamp
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
                .update({"conversation_history": supabase.fn.array_append('conversation_history', message_data)})\
                .eq("reference", from_number)\
                .execute()
        
        return {"status": "success", "message": "Message saved successfully"}
        
    except Exception as e:
        print("===ERROR===")
        print(e)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("api_whatsapp:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
