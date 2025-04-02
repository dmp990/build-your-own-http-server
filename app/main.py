import socket  # noqa: F401

CRLF = "\r\n"

# Mapping of response status code to 'status_code status_text'
# e.g. 200 -> 200 OK
response_status_to_text = {
    "200": "200 OK",
    "404": "404 Not Found"
}

def recv_and_parse_request(conn, bufsize=1024):
    data = conn.recv(bufsize)
    first_line = data.decode("utf-8").split(CRLF)[0]

    method, path, http_version = first_line.split(" ")

    return method, path, http_version

def get_response(path):
    message = "HTTP/1.1 "
    if path == "/":
        message += response_status_to_text["200"]
    else:
        message += response_status_to_text["404"]

    message += CRLF + CRLF
    return message.encode()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    URL, PORT = "localhost", 4221
    server_socket = socket.create_server((URL, PORT), reuse_port=False) # CHANGE REUSEPORT TO TRUE BEFORE SUBMISSION

    try:
        while True:
            print(f"Server waiting on {URL}:{PORT}")
            conn, addr = server_socket.accept() # wait for client
            print(f"Connected by {addr}")
            
            method, path, http_version = recv_and_parse_request(conn)

            response = get_response(path)
            
            conn.send(response)

            conn.close()
    except KeyboardInterrupt:
        print("Keyboard interrupt. Shutting down server")
    finally:
        server_socket.close()
        print("Server socket closed.")


if __name__ == "__main__":
    main()
