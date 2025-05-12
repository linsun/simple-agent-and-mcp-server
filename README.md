# Model Context Protocol (MCP) Server & Agent

A simple implementation of a Model Context Protocol server that manages context data for AI models.

## Setup

1. Install the required dependencies:
```bash
uv venv
uv pip install -r requirements.txt
```

2. Run the server:
```bash
uv run server.py
```

The server will start on `localhost:8080`.

## API Endpoints

### Store Context
```bash
curl -X POST http://localhost:8080/mcp/context \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "example-context",
    "data": {
      "key": "value",
      "metadata": "example"
    }
  }'
```

### Get Context
```bash
curl -X GET http://localhost:8080/mcp/context/example-context
```

### Delete Context
```bash
curl -X DELETE http://localhost:8080/mcp/context/example-context
```
### list all the tools
```bash
curl -X GET http://localhost:8080/mcp/tools
```

## Run the agent

```bash
OPENAI_API_KEY=$OPENAI_API_KEY uv run agent.py 
```

Sample output:
```text
Connected to server
LLM decided to use: calculator
Reasoning: The user is asking for the sum of 5 and 3, which is a basic arithmetic operation suitable for the calculator tool.
Tool 'calculator' executed with result: {'status': 'success', 'result': 8}

Final result: {'status': 'success', 'result': 8}
LLM decided to use: calculator
Reasoning: The user requested to multiply two numbers, so a calculator tool is appropriate to perform this arithmetic operation.
Tool 'calculator' executed with result: {'status': 'success', 'result': 24}

Final result: {'status': 'success', 'result': 24}
Disconnected from server
```
