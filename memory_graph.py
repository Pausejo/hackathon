import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage

from langgraph.graph import END
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START

import logging

logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv

load_dotenv()

# In memory
conn = sqlite3.connect(":memory:", check_same_thread = False)
os.makedirs("./state_db", exist_ok=True)

db_path = "./state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

model = ChatOpenAI(model="gpt-4o",temperature=0)


class State(MessagesState):
    summary: str

# Define the logic to call the model
def call_model(state: State):
    
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it
    if summary:
        
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"

        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]
    
    else:
        messages = state["messages"]
    
    response = model.invoke(messages)
    return {"messages": response}

def summarize_conversation(state: State):
    
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt 
    if summary:
        
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
        
    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)
    
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

def assistant(state: MessagesState):
    logging.info(f"Messages sent to model: {state['messages']}")
    result = {"messages": [llm_with_tools.invoke(state["messages"])]}
    logging.info(f"Result: {result}")
    return result

# Determine whether to end or summarize the conversation
def should_continue(state: State):
    
    """Return the next node to execute."""
    
    messages = state["messages"]
    
    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"
    
    # Otherwise we can just end
    return "assistant"



def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b

def clima() -> str:
    """Get the current weather in a given city."""
    return "templado" 

def web_browser():
    pass
   
tools = [add, multiply, divide, clima]
llm_with_tools = model.bind_tools(tools, parallel_tool_calls=False)


from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

def get_graph():
    # Define a new graph
    workflow = StateGraph(State)
    workflow.add_node("conversation", call_model)
    workflow.add_node(summarize_conversation)
    workflow.add_node("assistant", assistant)
    workflow.add_node("tools", ToolNode(tools))


    # Set the entrypoint as conversation
    workflow.add_edge(START, "conversation")
    workflow.add_conditional_edges("conversation", should_continue)
    workflow.add_edge("summarize_conversation", "assistant")
    workflow.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    workflow.add_edge("tools", "assistant")



    # Compile
    graph = workflow.compile(checkpointer=memory)

    return graph




# # Create a thread
# config = {"configurable": {"thread_id": "1"}}


# # Start conversation
# input_message = HumanMessage(content="hi! I'm Joan")
# output = get_graph().invoke({"messages": [input_message]}, config) 
# for m in output['messages'][-1:]:
#     m.pretty_print()

# input_message = HumanMessage(content="what's my name?")
# output = get_graph().invoke({"messages": [input_message]}, config) 
# for m in output['messages'][-1:]:
#      m.pretty_print()
