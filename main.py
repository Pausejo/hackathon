from llama_index.llms.mistralai import MistralAI
from llama_index.core.llms import ChatMessage
from llama_index.llms.mistralai import MistralAI


# To customize your API key, do this
# otherwise it will lookup MISTRAL_API_KEY from your env variable
# llm = MistralAI(api_key="<api_key>")

class ChatBot:
    def __init__(self):
        self.llm = MistralAI(api_key="<replace-with-your-key>")

    def chat(self, messages):
        if not messages:
            messages = [
                ChatMessage(role="system", content="You are CEO of MistralAI."),
                ChatMessage(role="user", content="Tell me the story about La plateforme"),
        ]
        resp = MistralAI().chat(messages) 

        return resp       


