from shared.websocket.schemas import WSMessage, WSSubscribe, WSPushNotificationS


def parse_ws_message(data: dict):
    action = data.get("action")
    if action == "subscribe":
        return WSSubscribe(**data)
    elif action == "message":
        return WSMessage(**data)
    else:
        raise ValueError(f"Unknown action: {action}")
