import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

class SimpleAgent:
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
        self.session = None
        # Load API key from environment variable
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def connect(self):
        """Establish a connection to the server"""
        self.session = aiohttp.ClientSession()
        print("Connected to server")

    async def close(self):
        """Close the connection"""
        if self.session:
            await self.session.close()
            print("Disconnected from server")

    async def get_available_tools(self) -> Dict[str, Any]:
        """Get list of available tools from the server"""
        if not self.session:
            await self.connect()
        async with self.session.get(f"{self.server_url}/mcp/tools") as response:
            return await response.json()

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if not self.session:
            await self.connect()

        async with self.session.post(
            f"{self.server_url}/mcp/tools/{tool_name}",
            json=parameters
        ) as response:
            result = await response.json()
            print(f"Tool '{tool_name}' executed with result: {result}")
            return result

    async def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process natural language input using LLM"""
        # Get available tools
        tools_response = await self.get_available_tools()
        tools = tools_response.get("tools", {})

        # Create a system message that describes the available tools
        system_message = {
            "role": "system",
            "content": f"""You are a helpful assistant that can use tools. 
            Your task is to analyze the user's request and determine which tool to use.
            Available tools: {json.dumps(tools, indent=2)}
            
            Respond in JSON format with the following structure:
            {{
                "tool_name": "name of the tool to use",
                "parameters": {{
                    // parameters for the tool
                }},
                "reasoning": "brief explanation of why this tool was chosen"
            }}
            """
        }

        # Get LLM's decision using the new API
        response = await self.client.chat.completions.create(
            model="gpt-4.1-mini",  # Changed to gpt-4.1-mini
            messages=[
                system_message,
                {"role": "user", "content": user_input}
            ],
            temperature=0.1  # Lower temperature for more consistent tool selection
        )

        try:
            # Parse the LLM's response
            tool_decision = json.loads(response.choices[0].message.content)
            print(f"LLM decided to use: {tool_decision['tool_name']}")
            print(f"Reasoning: {tool_decision['reasoning']}")

            # Execute the chosen tool
            return await self.execute_tool(
                tool_decision["tool_name"],
                tool_decision["parameters"]
            )
        except json.JSONDecodeError:
            print("Error: LLM response was not valid JSON")
            return {"status": "error", "message": "Failed to parse LLM response"}
        except Exception as e:
            print(f"Error executing tool: {str(e)}")
            return {"status": "error", "message": str(e)}

async def main():
    # Create the agent
    agent = SimpleAgent()
    
    try:
        # Connect to the server
        await agent.connect()

        # Example: Process natural language input
        result = await agent.process_input("What is 5 plus 3?")
        print("\nFinal result:", result)

        # Another example
        result = await agent.process_input("Multiply 4 by 6")
        print("\nFinal result:", result)

    finally:
        # Always close the connection
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main()) 