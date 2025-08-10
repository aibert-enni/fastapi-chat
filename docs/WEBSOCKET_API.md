# WebSocket Chat API Documentation

## Connection

**Endpoint:** `ws://localhost:8000/chats/ws`

**Authentication:** JWT token via query parameter

```
ws://localhost:8000/chats/ws?token=your_jwt_token_here
```

## Message Format

All messages are JSON objects sent as text frames.

### Client → Server Messages

#### Subscribe to Chats
```json
{
  "action": "subscribe",
  "chat_ids": ["chat-uuid-1", "chat-uuid-2"]
}
```

**Response:**
```json
{
  "action": "subscribe_response",
  "results": [
    {"chat_id": "chat-uuid-1", "status": "success"},
    {"chat_id": "chat-uuid-2", "status": "error", "error": "no access"}
  ]
}
```

#### Send Message
```json
{
  "action": "message",
  "chat_id": "chat-uuid",
  "text": "Hello, world!"
}
```

**Response:**
```json
{
  "action": "message_response",
  "status": "success"
}
```

### Server → Client Messages

#### Incoming Chat Message
```json
{
  "from": "username",
  "message": "Hello, world!",
  "chat_id": "chat-uuid",
}
```

#### Error Messages
```json
{
  "error": "Unknown action",
  "status": "error"
}
```

## Error Codes

| Error | Description |
|-------|-------------|
| `Unknown action` | Invalid action type |
| `no access` | User doesn't have access to chat |
| `Couldn't send message` | Message delivery failed |
| `Missing chat_id` | Required field missing |
| `Message cannot be empty` | Empty message text |

## Connection States

- **Connecting:** WebSocket handshake in progress
- **Connected:** Ready to send/receive messages
- **Disconnected:** Connection closed (code 1001 for normal closure)

## Example Usage

### JavaScript Client
```javascript
const ws = new WebSocket('ws://localhost:8000/chats/ws?token=' + token);

ws.onopen = function() {
    // Subscribe to chats
    ws.send(JSON.stringify({
        action: 'subscribe',
        chat_ids: ['chat-uuid-1']
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send a message
ws.send(JSON.stringify({
    action: 'message',
    chat_id: 'chat-uuid-1',
    text: 'Hello!'
}));
```

### Python Client
```python
import asyncio
import websockets
import json

async def chat_client():
    uri = "ws://localhost:8000/chats/ws?token=your_token"
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to chat
        await websocket.send(json.dumps({
            "action": "subscribe",
            "chat_ids": ["chat-uuid-1"]
        }))
        
        # Send message
        await websocket.send(json.dumps({
            "action": "message", 
            "chat_id": "chat-uuid-1",
            "text": "Hello from Python!"
        }))
        
        # Listen for messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(chat_client())
```

## Rate Limiting

- No explicit rate limits currently implemented
- Connection will be closed on malformed JSON or authentication errors

## Testing

Use tools like:
- **Browser DevTools** WebSocket tab
- **Postman** WebSocket collections  
- **wscat**: `wscat -c "ws://localhost:8000/chats/ws?token=TOKEN"`