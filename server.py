#Task2

#BY:
#Taima Nasser && Malak Milhem

from socket import *
import os

#student ID =1220031
Port = 9901  # socket server port number

def run_server():
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('', Port))
	# listen for requests
    serverSocket.listen(5)

    print('Web Server listening ...')
    while True:
        connection_socket, client_address = serverSocket.accept()
        request = connection_socket.recv(1024).decode('utf-8')  # Receive the request from the client
        handle_request(connection_socket, client_address, request)  # Handle the request
        connection_socket.close()  # Close the connection after handling the request


def parse_request(request):
    parts = request.split("\n")  # Split the request by lines
    if len(parts) == 0:
        raise ValueError("Empty request")  # Raise error if the request is empty
    request_line = parts[0].split()  # Split the first line of the request into parts
    if len(request_line) < 2:
        raise ValueError("Invalid request line")  #if the request line invalid
    method = request_line[0]  # Get the HTTP method 
    file_path = request_line[1][1:]  # Get the file path
    return method, file_path  

def send_response(connectionSocket, status, content_type, content):
    # Build the response header with status and content type
    response = f"HTTP/1.1 {status}\r\nContent-Type: {content_type}; charset=utf-8\r\n\r\n"
    connectionSocket.send(response.encode('utf-8'))  # Send the header
    if isinstance(content, str):  # If content is a string, encode and send it
        connectionSocket.send(content.encode('utf-8'))
    else:  # If content is binary , send it directly
        connectionSocket.send(content)

    print(f"Response sent: {status} | Content-Type: {content_type}")

def handle_request(connection_socket, client_address, request):
    content_types = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpeg",
    }
    print(f"Received HTTP request from {client_address}:\n")
    print(request) #print reguest details
    try:
       # Parse the request to get the method and file path
       method, file_path = parse_request(request)
    except ValueError as e:
       # If there's an error in parsing client's input send a 400 response
       send_response(connection_socket, "400 Bad Request", "text/html", str(e))
       return

    if method == "GET": # GET requests for images and videos
        if "file-name=" in file_path:
            # Extract query parameters from the file path (URL)
            query_params = file_path.split('?')[1]
            params = dict(item.split('=') for item in query_params.split('&'))
            file_name = params.get('file-name', '')  # Get the file name
            file_type = params.get('file-type', '')  # Get the file type (image or video)

            if file_name:
                # Redirect to Google Images if it's an image request
                if file_type == 'image':
                    location = f"https://www.google.com/search?q={file_name}&tbm=isch"
                    response = f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {location}\r\n\r\n"
                    connection_socket.send(response.encode('utf-8'))
                # Redirect to YouTube if it's a video request
                elif file_type == 'video':
                    location = f"https://www.youtube.com/results?search_query={file_name}"
                    response = f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {location}\r\n\r\n"
                    connection_socket.send(response.encode('utf-8'))
                else:
                    # If the file type is invalid, send a 400 Bad Request
                    send_response(connection_socket, "400 Bad Request", "text/html", "Invalid file type.")
            else:
                # If the file name is missing, send a 400 Bad Request
                send_response(connection_socket, "400 Bad Request", "text/html", "File name is required.")
            return

    # Handle GET requests for other files 
    if file_path in ["", "index.html", "en"]:
        file_path = "main_en.html"  # Default to main_en.html 
    elif file_path == "ar":
        file_path = "main_ar.html"  # Serve the Arabic version if requested

    # If the file exists, send it to the client
    if os.path.isfile(file_path):
        file_extension = file_path.split(".")[-1]  # Get the file extension
        content_type = content_types.get(file_extension, "text/plain")  # Get content type

        # Open the file and send its content
        with open(file_path, "rb") as f:
            content = f.read()
        send_response(connection_socket, "200 OK", content_type, content)
    else:
        # If the file doesn't exist, send a 404 Not Found error with a custom error page
        with open("error.html", "r", encoding="utf-8") as f:
            error_content = f.read()
            # the error page with the client's IP and port
            error_content = error_content.replace('<p id="client-info"></p>', f"<p>Client's IP: {client_address[0]}</p><p>Client's Port: {client_address[1]}</p>")
        send_response(connection_socket, "404 Not Found", "text/html", error_content)


if __name__ == "__main__":
    run_server()