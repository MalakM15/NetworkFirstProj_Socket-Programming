#Task2
#BY:
#Taima Nasser && Malak Milhem

from socket import *
import os

#student ID =1220031
Port = 9901  # socket server port number

# Get base directory and static folder path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {BASE_DIR}")


def run_server():
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('', Port))
	# listen for requests
    serverSocket.listen(5)

    print('Web Server listening ...')
    while True:
        connection_socket, client_address = serverSocket.accept()
        request = connection_socket.recv(1024).decode('utf-8')  # Receive the request from the client

        if not request.strip():  # Skip if request is empty or whitespace
            print(" Empty request received, skipping.")
            connection_socket.close()
            continue

        handle_request(connection_socket, client_address, request)  
        #connection_socket.close() 


def parse_request(request):
    parts = request.split("\n")  # split the request by lines
    if len(parts) == 0:
        raise ValueError("Empty request")  # error if the request is empty
    request_line = parts[0].split()  
    if len(request_line) < 2:
        raise ValueError("Invalid request line")  #if the request line invalid
    method = request_line[0]  # Get the HTTP method 
    file_path = request_line[1][1:]  # Get the file path
    return method, file_path  

def send_response(connectionSocket, status, content_type, content, client_address=None):
    try:
        # Build the response header with status and content type
        response = f"HTTP/1.1 {status}\r\nContent-Type: {content_type}; charset=utf-8\r\n\r\n"
        connectionSocket.send(response.encode('utf-8'))  # Send the header

        # If it's a 404 error, generate HTML page
        if status == "404 Not Found" and client_address:
            ip, port = client_address
            content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error 404</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin-top: 50px;
                    }}
                    .error-message {{
                        color: red;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                    .client-info {{
                        margin-top: 20px;
                        font-size: 18px;
                    }}
                </style>
            </head>
            <body>
                <h1 class="error-message">The file is not found</h1>
                <div class="client-info">
                    Client IP: {ip}<br>
                    Client Port: {port}
                </div>
            </body>
            </html>
            """
        # Send the content
        if isinstance(content, str):  # If content is a string, encode and send it
            connectionSocket.send(content.encode('utf-8'))
        else:  # If content is binary, send it directly
            connectionSocket.send(content)

        print(f"Response sent: {status} | Content-Type: {content_type}")
    except ConnectionAbortedError:
        print("! Client closed the connection before the server could send the response.")
    except Exception as e:
        print(f"! Unexpected error while sending response: {e}")

def handle_request(connection_socket, client_address, request):
    content_types = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpeg",
    }
    print(f"Received HTTP request from {client_address}:\n")
    print(request)  # Print request details
    try:
        # Parse the request to get the method and file path
        method, file_path = parse_request(request)
    except ValueError as e:
        # If there's an error in parsing client's input, send a 400 response
        send_response(connection_socket, "400 Bad Request", "text/html", str(e))
        return  # Stop further processing

    if method == "GET":  # handle GET requests
        if "file-name=" in file_path:
            # Extract query parameters from the file path (URL)
            query_params = file_path.split('?')[1]
            params = dict(item.split('=') for item in query_params.split('&'))
            file_name = params.get('file-name', '')  # Get the file name
            file_type = params.get('file-type', '')  # Get the file type (image or video)

            if file_name:
                # Redirect to google Images if it's an image request
                if file_type == 'image':
                    location = f"https://www.google.com/search?tbm=isch&q={file_name}"
                    response = (
                        f"HTTP/1.1 307 Temporary Redirect\r\n"
                        f"Location: {location}\r\n"
                        f"Content-Length: 0\r\n"
                        f"Connection: close\r\n"
                        f"\r\n"
                    )
                    connection_socket.send(response.encode('utf-8'))
                    return
                
                elif file_type == 'video':
                    location = f"https://www.google.com/search?tbm=vid&q={file_name}"
                    response = (
                        f"HTTP/1.1 307 Temporary Redirect\r\n"
                        f"Location: {location}\r\n"
                        f"Content-Length: 0\r\n"
                        f"Connection: close\r\n"
                        f"\r\n"
                    )
                    connection_socket.send(response.encode('utf-8'))
                    return  
                else:
                    # If the file type is invalid, send a 400 Bad Request
                    send_response(connection_socket, "400 Bad Request", "text/html", "Invalid file type.")
                    return 
            else:
                # If the file doesn't exist, send a 404 Not Found error
                print(f"File not found: {file_path}")
                send_response(connection_socket, "404 Not Found", "text/html", "<h1>404 Not Found</h1>")
                return  

    # Handle GET requests for other files
    if file_path in ["", "index.html", "en"]:
        file_path = "main_en.html"  # Default to main_en.html
    elif file_path == "ar":
        file_path = "main_ar.html"  # Serve the Arabic version if requested

    # Clean up path and get full file path
    file_path = file_path.lstrip('/')  # Remove leading slash
    full_path = os.path.join(BASE_DIR, file_path) 

    print(f"Requested file path: {file_path}")
    print(f"Full file path: {full_path}")
    print(f"File exists: {os.path.isfile(full_path)}")

    if os.path.isfile(full_path):
        try:
            print("Found file, attempting to open...")
            file_extension = full_path.split(".")[-1]  # Get the file extension
            content_type = content_types.get(file_extension, "application/octet-stream")

            # Use 'rb' for binary files and 'r' for text files
            if file_extension in ["png", "jpg"]:
                mode = 'rb'
                with open(full_path, mode) as f:
                    content = f.read()
            else:
                mode = 'r'
                with open(full_path, mode, encoding='utf-8') as f:
                    content = f.read()

            send_response(connection_socket, "200 OK", content_type, content)
            return 
        except Exception as e:
            print(f"Error opening file: {e}")
            send_response(connection_socket, "500 Internal Server Error", "text/html", "<h1>500 Internal Server Error</h1>")
            return
    else:
        # If the file doesn't exist, send a 404 Not Found error
        print(f"File not found: {full_path}")
        send_response(connection_socket, "404 Not Found", "text/html", None, client_address)
        return  



if __name__ == "__main__":
    run_server()

