import socket  # noqa: F401

CRLF = "\r\n"

# Mapping of response status code to 'status_code status_text'
# e.g. 200 -> 200 OK
response_status_to_text = {
    "200": "200 OK",
    "404": "404 Not Found"
}

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False) # CHANGE REUSEPORT TO TRUE BEFORE SUBMISSION

    
    conn, addr = server_socket.accept() # wait for client
    print(f"Connected by {addr}")
    data = conn.recv(1024) # Read upto 1024 bytes
    requested_resource = data.decode("utf-8").split(CRLF)[0].split(" ")[1]

    message = "HTTP/1.1 "
    if requested_resource == "/":
        message += response_status_to_text["200"]
    else:
        message += response_status_to_text["404"]

    message += CRLF + CRLF
    conn.send(message.encode())


if __name__ == "__main__":
    main()
