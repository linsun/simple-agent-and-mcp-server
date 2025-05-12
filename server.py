import asyncio
import json
from aiohttp import web
from typing import Dict, Any, Optional

class MCPServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.contexts: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {
            "calculator": {
                "name": "calculator",
                "description": "A simple calculator tool that can perform basic arithmetic operations",
                "parameters": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                }
            }
        }

    def setup_routes(self):
        self.app.router.add_get('/', self.hello_world)
        self.app.router.add_post('/mcp/context', self.handle_context_request)
        self.app.router.add_get('/mcp/context/{context_id}', self.get_context)
        self.app.router.add_delete('/mcp/context/{context_id}', self.delete_context)
        self.app.router.add_get('/mcp/tools', self.list_tools)
        self.app.router.add_post('/mcp/tools/{tool_name}', self.execute_tool)

    async def hello_world(self, request):
        return web.json_response({
            "message": "Hello World from MCP Server!",
            "status": "running"
        })

    async def list_tools(self, request):
        return web.json_response({
            "status": "success",
            "tools": self.tools
        })

    async def execute_tool(self, request):
        try:
            tool_name = request.match_info['tool_name']
            if tool_name not in self.tools:
                return web.json_response({
                    "status": "error",
                    "message": f"Tool {tool_name} not found"
                }, status=404)

            data = await request.json()
            
            if tool_name == "calculator":
                operation = data.get('operation')
                a = data.get('a')
                b = data.get('b')
                
                if not all([operation, a is not None, b is not None]):
                    return web.json_response({
                        "status": "error",
                        "message": "Missing required parameters"
                    }, status=400)

                result = None
                if operation == "add":
                    result = a + b
                elif operation == "subtract":
                    result = a - b
                elif operation == "multiply":
                    result = a * b
                elif operation == "divide":
                    if b == 0:
                        return web.json_response({
                            "status": "error",
                            "message": "Division by zero"
                        }, status=400)
                    result = a / b

                return web.json_response({
                    "status": "success",
                    "result": result
                })

            return web.json_response({
                "status": "error",
                "message": f"Tool {tool_name} not implemented"
            }, status=501)

        except Exception as e:
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=400)

    async def handle_context_request(self, request):
        try:
            data = await request.json()
            
            # Validate required fields
            if 'context_id' not in data:
                return web.json_response({
                    "status": "error",
                    "message": "context_id is required"
                }, status=400)

            context_id = data['context_id']
            context_data = data.get('data', {})
            
            # Store the context
            self.contexts[context_id] = {
                "data": context_data,
                "timestamp": asyncio.get_event_loop().time()
            }

            return web.json_response({
                "status": "success",
                "message": "Context stored successfully",
                "context_id": context_id
            })

        except Exception as e:
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=400)

    async def get_context(self, request):
        try:
            context_id = request.match_info['context_id']
            if context_id not in self.contexts:
                return web.json_response({
                    "status": "error",
                    "message": f"Context {context_id} not found"
                }, status=404)

            return web.json_response({
                "status": "success",
                "context": self.contexts[context_id]
            })

        except Exception as e:
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=400)

    async def delete_context(self, request):
        try:
            context_id = request.match_info['context_id']
            if context_id not in self.contexts:
                return web.json_response({
                    "status": "error",
                    "message": f"Context {context_id} not found"
                }, status=404)

            del self.contexts[context_id]
            return web.json_response({
                "status": "success",
                "message": f"Context {context_id} deleted successfully"
            })

        except Exception as e:
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=400)

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"MCP Server running at http://{self.host}:{self.port}")

async def main():
    server = MCPServer()
    await server.start()
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour

if __name__ == "__main__":
    asyncio.run(main()) 