#Task2

#BY:
#Taima Nasser && Malak Milhem

from socket import *
import os

#student ID =1220031
Port = 9901  # socket server port number

# Get base directory and static folder path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

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
            print("⚠️ Empty request received, skipping.")
            connection_socket.close()
            continue

        handle_request(connection_socket, client_address, request)  
        #connection_socket.close()  # Close the connection after handling the request


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
    try: 
       # Build the response header with status and content type
       response = f"HTTP/1.1 {status}\r\nContent-Type: {content_type}; charset=utf-8\r\n\r\n"
       connectionSocket.send(response.encode('utf-8'))  # Send the header
       if isinstance(content, str):  # If content is a string, encode and send it
           connectionSocket.send(content.encode('utf-8'))
       else:  # If content is binary , send it directly
           connectionSocket.send(content)

       print(f"Response sent: {status} | Content-Type: {content_type}")
    except ConnectionAbortedError:
           print("⚠️ Client closed the connection before the server could send the response.")
    except Exception as e:
           print(f"⚠️ Unexpected error while sending response: {e}")
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
                    location = f"https://www.google.com/search?tbm=isch&q={file_name}"
                    #location = f"https://www.google.com/search?q={file_name}&udm=2"

                    response = (
                        f"HTTP/1.1 307 Temporary Redirect\r\n"
                        f"Location: {location}\r\n"
                        f"Content-Length: 0\r\n"
                        f"Connection: close\r\n"
                        f"\r\n"
                    )
                    connection_socket.send(response.encode('utf-8'))
                # Redirect to YouTube if it's a video request
                elif file_type == 'video':
                    location =  f"https://www.google.com/search?tbm=vid&q={file_name}"
                    response = (
                        f"HTTP/1.1 307 Temporary Redirect\r\n"
                        f"Location: {location}\r\n"
                        f"Content-Length: 0\r\n"
                        f"Connection: close\r\n"
                        f"\r\n"
                    )
                    connection_socket.send(response.encode('utf-8'))
                else:
                    # If the file type is invalid, send a 400 Bad Request
                    send_response(connection_socket, "400 Bad Request", "text/html", "Invalid file type.")
                    return
            else:
                # If the file name is missing, send a 400 Bad Request
                send_response(connection_socket, "400 Bad Request", "text/html", "File name is required.")
            return

    # Handle GET requests for other files 
    if file_path in ["", "index.html", "en"]:
        file_path = "/main_en.html"  # Default to main_en.html 
    elif file_path == "ar":
        file_path = "main_ar.html"  # Serve the Arabic version if requested

    # Clean up path and get full file path
    file_path = file_path.lstrip('/')  # remove leading slash
    full_path = os.path.join(STATIC_DIR, file_path)


    # If the file exists, send it to the client
    if os.path.isfile(file_path):
        print ("found file @@")
        file_extension = file_path.split(".")[-1]  # Get the file extension
        content_type = content_types.get(file_extension, "text/plain")  # Get content type

        # Open the file and send its content
        with open(file_path, 'r') as f:
            content = f.read()
        send_response(connection_socket, "200 OK", content_type, content)
    else:
        # If the file doesn't exist, send a 404 Not Found error with a custom error page
        #with open("error.html", "r", encoding="utf-8") as f:
        #    error_content = f.read()
            # the error page with the client's IP and port
            #error_content = error_content.replace('<p id="client-info"></p>', f"<p>Client's IP: {client_address[0]}</p><p>Client's Port: {client_address[1]}</p>")
        #send_response(connection_socket, "404 Not Found", "text/html", error_content)
        content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Server Error</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #fff0f0;
                    text-align: center;
                    padding: 60px;
                }
                h1 {
                    font-size: 48px;
                    color: #cc0000;
                }
                p {
                    font-size: 18px;
                    color: #555;
                }
            </style>
        </head>
        <body>
            <h1>500 Internal Server Error</h1>
            <p>Sorry, something went wrong on the server.</p>
        </body>
        </html>
        """
        send_response(connection_socket, "500 Internal Server Error", "text/html", content)

if __name__ == "__main__":
    run_server()