from pydantic import EmailStr
import asyncio
import json
from fastmcp import Client
from langchain_google_genai import GoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from langchain.tools import BaseTool
from pydantic import BaseModel, ConfigDict

client = Client("http://localhost:8000/mcp")


class AddInput(BaseModel):
    a: int
    b: int


class EmailInput(BaseModel):
    to: str
    subject: str
    body: str


async def call_mcp_tool(tool_name: str, **kwargs):
    async with client:
        response = await client.call_tool(
            tool_name,
            arguments=kwargs   # ✅ THIS is the key fix
        )
    return response


async def get_all_tools():
    async with client:
        return await client.list_tools()


mcp_tools = asyncio.run(get_all_tools())
print(f"Available MCP Tools: {[tool.name for tool in mcp_tools]}")


class MCPTool(BaseTool):
    name: str
    description: str
    args_schema: type[BaseModel]
    mcp_tool_name: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, **kwargs) -> str:
        print(f"[SYNC] Calling {self.mcp_tool_name} with {kwargs}")

        result = asyncio.run(call_mcp_tool(self.mcp_tool_name, **kwargs))

        print("RAW MCP RESULT:", result)  # keep this for debugging

        # ✅ STRICT NORMALIZATION
        try:
            return result["content"][0]["text"]
        except Exception:
            return str(result)

    async def _arun(self, **kwargs) -> str:
        print(f"[ASYNC] Calling {self.mcp_tool_name} with {kwargs}")
        return await call_mcp_tool(self.mcp_tool_name, **kwargs)


tools = [
    MCPTool(
        name="add",
        description="Add two numbers",
        args_schema=AddInput,
        mcp_tool_name="add"
    ),
    MCPTool(
        name="send_email",
        description="Send an email",
        args_schema=EmailInput,
        mcp_tool_name="send_email"
    )
]


model = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.0,
    max_retries=2,
    api_key="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"
)


agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="""
You are an AI agent.

Rules:
- Use tools when needed
- After completing all tasks, ALWAYS return a final answer
- If an email is sent, confirm it and STOP
"""
)


user_input = "Calculate Sum of 5+4 and then send email to zeeshan@gmail.com the result"
response = agent.invoke(
    {"messages": [{"role": "user", "content": user_input}]},
    config={"configurable": {"thread_id": "user123"}}
)

print(response["messages"][-1].content if "messages" in response else response)
