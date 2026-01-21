import asyncio
import json
import os

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role

async def main():

    #TODO:
    # 1. Create MCP client with `docker_image="mcp/duckduckgo:latest"` as `mcp_client`
    async with MCPClient(docker_image="mcp/duckduckgo:latest") as mcp_client:
    # 2. Get Available MCP Tools, assign to `tools` variable, print tool as well
        tools = await mcp_client.get_tools()
        print("Available MCP Tools:")
        for tool in tools:
            print(json.dumps(tool, indent=2))
    # 3. Create DialClient:
    #       - api_key=os.getenv("DIAL_API_KEY")
    #       - endpoint="https://ai-proxy.lab.epam.com"
    #       - tools=tools
    #       - mcp_client=mcp_client
        dial_client = DialClient(
            api_key=os.getenv("DIAL_API_KEY"),
            endpoint="https://ai-proxy.lab.epam.com",
            tools=tools,
            mcp_client=mcp_client,
        )
    # 4. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
        messages = [
            Message(
                role=Role.SYSTEM,
                content="You are an intelligent assistant that can use tools to answer user queries."
            )
        ]
    # 5. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
        print("Welcome to the MCP-powered chat! Type 'exit' to quit.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting chat. Goodbye!")
                break

            messages.append(Message(role=Role.USER, content=user_input))

            response = await dial_client.get_completion(messages=messages)
            print(f"\nAssistant: {response.content}")

            messages.append(Message(role=Role.AI, content=response.content))


if __name__ == "__main__":
    asyncio.run(main())