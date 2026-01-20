import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

async def main():
    #TODO:
    # 1. Create MCP client and open connection to the MCP server (use `async with {YOUR_MCP_CLIENT} as mcp_client`),
    #    mcp_server_url="http://localhost:8005/mcp"
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8005/mcp")
    async with MCPClient(mcp_server_url) as mcp_client:
    # 2. Get Available MCP Resources and print them
        resources: list[Resource] = await mcp_client.session.list_resources()
        print("Available MCP Resources:")
        for resource in resources.resources:
            print(f"- {resource.name} (type: {resource.mimeType})")
    # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
        tools = await mcp_client.get_tools()
        print("\nAvailable MCP Tools:")
        for tool in tools:
            print(f"- {tool['function']['name']}: {tool['function']['description']}")
    # 4. Create DialClient
        dial_client = DialClient(
            api_key=os.getenv("DIAL_API_KEY"),
            endpoint="https://ai-proxy.lab.epam.com",
            tools=tools,
            mcp_client=mcp_client
            )
    # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
        messages: list[Message] = [
            Message(
                role=Role.SYSTEM,
                content=SYSTEM_PROMPT
            )
        ]
    # 6. Add to messages Prompts from MCP server as User messages
        prompts: list[Prompt] = await mcp_client.get_prompts()
        for prompt in prompts:
            prompt_content = await mcp_client.get_prompt(prompt.name)
            messages.append(
                Message(
                    role=Role.USER,
                    content=prompt_content
                )
            )
    # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
        print("\nWelcome to the User Management Agent Chat! Type 'exit' to quit.")
        while True:
            user_input = input("\nYour promopt: ")
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting chat. Goodbye!")
                break

            messages.append(
                Message(
                    role=Role.USER,
                    content=user_input
                )
            )

            ai_message: Message = await dial_client.get_completion(messages)
            messages.append(ai_message)

            print(f"\nAgent: {ai_message.content}")


if __name__ == "__main__":
    asyncio.run(main())
