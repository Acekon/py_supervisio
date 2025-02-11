import json
import socket
import time

from info import get_user_info, get_sys_info


with open("config.json", "r") as f:
    config = json.load(f)


def send_activity(data):
    host = config.get("host")
    port = config.get("port")
    path = "/api/v1/activity/"
    json_data = json.dumps(data)
    headers = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(json_data)}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{json_data}"
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(headers.encode())

    # check response
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    sock.close()
    response_text = response.decode()
    body = response_text.split("\r\n\r\n", 1)[1]
    print(body)


def main():
    user_info = get_user_info()
    sys_info = get_sys_info()
    body = {
        "user_sid": user_info.get("LastLoggedOnUserSID"),
        "user_name": user_info.get("LastLoggedOnUser"),
        "user_display_name": user_info.get("LastLoggedOnDisplayName"),
        "user_ip": sys_info.get('ip'),
        "sys_name": sys_info.get('sys_name'),
        "sys_version": json.dumps(sys_info.get('sys_version')),
        "timestamp": time.time(),
    }
    send_activity(body)


if __name__ == "__main__":
    main()
