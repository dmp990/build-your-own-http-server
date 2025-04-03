import socket  # noqa: F401
import threading
import os
import sys

HTTP_VER = "HTTP/1.1"
CRLF = "\r\n"
SP = " "

# Mapping of response status code to 'status_code status_text'
# e.g. 200 -> 200 OK
response_status_to_text = {"200": "200 OK", "404": "404 Not Found"}

endpoints = {
    "/": {
        "name": "index",
        "description": "Respond with 200 OK and empty response body",
        "response_status_line": HTTP_VER
        + SP
        + response_status_to_text["200"]
        + CRLF
        + CRLF,
    },
    "/echo/": {
        "name": "echo",
        "description": "Accept /{str} and return it in the response body",
        "response_status_line": HTTP_VER
        + SP
        + response_status_to_text["200"]
        + CRLF
        + CRLF,
        "response_headers": "Content-Type: text/plain"
        + CRLF
        + "Content-Length: 3"
        + CRLF
        + CRLF,
    },
}


def recv_and_parse_request(conn, bufsize=1024):
    data = conn.recv(bufsize)
    splitted = data.decode("utf-8").split(CRLF)

    first_line = splitted[0]
    method, path, http_version = first_line.split(" ")

    # Get headers
    headers = {}
    for line in splitted[1:]:
        if line == "":
            break
        key, value = line.split(":", 1)
        headers[key] = value.strip()

    return method, path, http_version, headers


def get_response(path, headers, directory):
    if path.startswith("/echo/"):
        msg = path[len("/echo/") :]
        body = msg
        content_length = len(body.encode())
        response_headers = (
            "Content-Type: text/plain"
            + CRLF
            + f"Content-Length: {content_length}"
            + CRLF
            + CRLF
        )
        endpoint = endpoints.get("/echo/")
        status_line = HTTP_VER + SP + response_status_to_text["200"] + CRLF
        return (status_line + response_headers + body + CRLF).encode()

    if path == "/user-agent":
        content_length = len(headers.get("User-Agent", "").encode())
        response_headers = (
            "Content-Type: text/plain"
            + CRLF
            + f"Content-Length: {content_length}"
            + CRLF
            + CRLF
        )
        body = headers.get("User-Agent", "")
        status_line = HTTP_VER + SP + response_status_to_text["200"] + CRLF
        return (status_line + response_headers + body + CRLF).encode()

    if path.startswith("/files/"):
        # print("handling /files")
        filename = path[len("/files/") :]

        # print("Filename:", filename)

        if not directory.strip():
            pass
        if not filename.strip():
            pass

        full_path = os.path.join(directory, filename)
        # print("Full path:", full_path, "Does it exist?", os.path.exists(full_path))
        
        # If file exists
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                content = f.read()
                status_line = HTTP_VER + SP + response_status_to_text["200"] + CRLF
                content_length = len(content)
                response_headers = (
                    "Content-Type: application/octet-stream"
                    + CRLF
                    + f"Content-Length: {content_length}"
                    + CRLF
                    + CRLF
                )
                return (status_line + response_headers).encode() + content
        else:
            return ("HTTP/1.1 " + response_status_to_text["404"] + CRLF + CRLF).encode() # Respond with 404

    endpoint = endpoints.get(path)
    if endpoint:
        return (
            endpoint["response_status_line"]
            + endpoint.get("response_headers", "")
            + CRLF
            + CRLF
        ).encode()

    message = "HTTP/1.1 " + response_status_to_text["404"] + CRLF + CRLF
    return message.encode()


def handle_client(conn, addr, directory):
    print(f"Connected by {addr}")

    method, path, http_version, headers = recv_and_parse_request(conn)

    response = get_response(path, headers=headers, directory=directory)

    conn.send(response)

    conn.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    directory = None
    if "--directory" in sys.argv:
        directory = sys.argv[sys.argv.index("--directory") + 1]

    # Uncomment this to pass the first stage
    #
    URL, PORT = "0.0.0.0", 4221
    server_socket = socket.create_server(
        (URL, PORT), reuse_port=False
    )  # CHANGE REUSEPORT TO TRUE BEFORE SUBMISSION

    try:
        while True:
            print(f"Server waiting on {URL}:{PORT}")
            conn, addr = server_socket.accept()  # wait for client

            thread = threading.Thread(
                target=handle_client, args=(conn, addr, directory)
            )

            thread.start()

            # thread.join()

    except KeyboardInterrupt:
        print("Keyboard interrupt. Shutting down server")
    finally:
        server_socket.close()
        print("Server socket closed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
