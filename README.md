# Model Context Protocol (MCP) Server

A simple implementation of a Model Context Protocol server that manages context data for AI models.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
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

## Features

- Store model context data with unique identifiers
- Retrieve stored context data
- Delete context data when no longer needed
- Timestamp tracking for context entries
- Async HTTP server using aiohttp
- JSON request/response handling
- Basic error handling
- Configurable host and port 