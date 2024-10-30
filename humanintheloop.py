from dotenv import load_dotenv
load_dotenv()

from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_community.document_loaders import SeleniumURLLoader
from langchain_core.tools import BaseTool


memory = MemorySaver()




class WebScrapeTool(BaseTool):
    name: str = "web_scrape"
    description: str = "Scrapes content from a given URL using Selenium"
    
    def _run(self, url: str) -> str:
        print("====Exec=====")
        url = "https://www.google.com/search?q=clima+hoy"
        loader = SeleniumURLLoader(urls=[url])
        docs = loader.load()
        # Combine all document content into a single string
        return "\n".join(doc.page_content for doc in docs)
    
    def _arun(self, url: str) -> str:
        raise NotImplementedError("Async not implemented")



class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


# tool = TavilySearchResults(max_results=2, include_domains=["support.guruwalk.com"])
tool = WebScrapeTool()
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(
    checkpointer=memory,
    # This is new!
    interrupt_before=["tools"],
    # Note: can also interrupt __after__ tools, if desired.
    # interrupt_after=["tools"]
)

user_input = "QClima hoy en Barcelona"
config = {"configurable": {"thread_id": "1"}}
# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)
print(snapshot.next)



# `None` will append nothing new to the current state, letting it resume as if it had never been interrupted
events = graph.stream(None, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()