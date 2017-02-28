"""Web service that acts as an HTTP proxy

+---------------------------------------------+
| Created and executed on Python 3.6.0, win32 |
+---------------------------------------------+

+---------------------------------------------------------------------+
| Resources I learned from (** denotes particularly useful resources) |
+---------------------------------------------------------------------+
- (YouTube video) "Basic concepts of web apps, how they work, & the HTTP protocol"
- (YouTube video) "REST API concepts and examples"
- (YouTube video) "What is REST?"
- (Website) httpbin.org
- (YouTube video) "Learning Python Web Penetration Testing: HTTP Proxy Anatomy | packtpub.com"
- (YouTube video) "HTTP Servers Part 2 [Python]" by SolidShellSecurity
- (Stack Overflow question) "Python  3.x BaseHTTPServer or http.server" by Learner
- **(YouTube series) "[urllib]" series by John Hammond**
- **(YouTube video) "Python 3 Programming Tutorial—Sockets intro" by sentdox**
- **luugiathuy.com -> Simple Web Proxy Python**
- **Python official documentation for urllib and socket**
- **Google images for HTTP request format and URL components**

+----------------+
| Specifications |
+----------------+
- Runs a HTTP web server on a specified hostname and port. Fulfills GET and POST requests by proxy, given a URL of the
  form http://HOSTNAME/.../ and data as key-value pairs

+-------------------------------+
| Opportunities for improvement |
+-------------------------------+
- Check the user input more thoroughly for validity and handle more undesirable cases/exceptions.
- Make timestamped server logs (logger & datetime.datetime.now())
- Check length of messages received and sent to ensure all data was transmitted.
- Handle common pages requests for favicons, images, and other such web elements.
- Make parsing more robust for POST requests (e.g. if data has double quotation marks it may not be parsed correctly).
- Make Control-C stop the program more reliably (possibly a threading issue, use Control-Break for best results).
- This server does not encrypt communications. To increase security and use HTTPS, I'd need an investigation spike.

+---------+
| Defects |
+---------+
- When using Windows command prompt 10.0.14393.0 and curl 7.53.0.0, the first line of this server's response is cut off
  (for httpbin.org/get, this first character is an opening curly bracket). This behaviour was not observed on Google
  Chrome, Microsoft Edge, Internet Explorer, or Postman, and so it has been logged as a defect.

  The expected response format can be achieved for Windows command line users by sending a newline ("\n") through the
  socket before the response (i.e. the first line will now be visible). Sending any other four characters (e.g. "\tF_0")
  through the socket before the response will result in the first line being visible, but with these four characters
  concatenated to the beginning of it. Any fewer than four characters and neither the characters nor the first line will
  show (that is, with the exception of the newline character).

+----------------------------+
| Test cases on command line |
+----------------------------+
- Test GET:
    Command: curl http://localhost:8000/proxy/http://httpbin.org/get
    Result:
      "args": {},
      "headers": {
        "Accept-Encoding": "identity",
        "Host": "httpbin.org",
        "User-Agent": "curl/7.53.0"
      },
      "origin": "70.49.146.147",
      "url": "http://httpbin.org/get"
    }

- Test POST with 1 key-value pair:
    Command: curl -X POST -d asdf=blah http://localhost:8000/proxy/http://httpbin.org/post
    Result:
      "args": {},
      "data": "",
      "files": {},
      "form": {
        "asdf": "blah"
      },
      "headers": {
        "Accept-Encoding": "identity",
        "Content-Length": "9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "httpbin.org",
        "User-Agent": "curl/7.53.0"
      },
      "json": null,
      "origin": "70.49.146.147",
      "url": "http://httpbin.org/post"
    }

- Test POST with 2 key-value pairs and single quotation marks for data value:
    Command: curl -X POST -d asdf=blah -d squa='skrr' http://localhost:8000/proxy/http://httpbin.org/post
    Result:
      "args": {},
      "data": "",
      "files": {},
      "form": {
        "asdf": "blah",
        "squa": "skrr"
      },
      "headers": {
        "Accept-Encoding": "identity",
        "Content-Length": "19",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "httpbin.org",
        "User-Agent": "curl/7.53.0"
      },
      "json": null,
      "origin": "70.49.146.147",
      "url": "http://httpbin.org/post"
    }

- Test POST with 2 key-value pairs, single and double quotation marks for data value and key
    Command: curl -X POST -d "asdf"="blah" -d 'squa'='skrr' http://localhost:8000/proxy/http://httpbin.org/post
    Result:
      "args": {},
      "data": "",
      "files": {},
      "form": {
        "asdf": "blah",
        "'squa": "skrr'"
      },
      "headers": {
        "Accept-Encoding": "identity",
        "Content-Length": "19",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "httpbin.org",
        "User-Agent": "curl/7.53.0"
      },
      "json": null,
      "origin": "70.49.146.147",
      "url": "http://httpbin.org/post"
    }

+-----------------------------------------+
| Test cases on Google Chrome address bar |
+-----------------------------------------+
- Test GET:
    URL: http://localhost:8000/proxy/http://httpbin.org/get
    Result:
    {
      "args": {},
      "headers": {
        "Accept-Encoding": "identity",
        "Host": "httpbin.org",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
      },
      "origin": "70.49.146.147",
      "url": "http://httpbin.org/get"
    }

- Test GET on Google.ca
    URL: http://localhost:8000/proxy/http://www.google.ca
    Result (qualitative): Loaded page without pictures. Server received multiple requests it was not able to fulfill due
                          to the page specifying neither "/proxy/" nor a hostname in the URL of each request.

- Test GET on a foreign domain:
    URL: http://localhost:8000/proxy/http://www.thelocal.fr/
    Result (qualitative): Same as the above case (Google.ca)

- Test GET with HTTPS:
    URL: http://localhost:8000/proxy/https://www.linkedin.com/
    Result (qualitative): Page appeared to load perfectly, pictures, favicon, and all. Server received several requests
                          it could not handle, all of which appeared related to "tokens" and user tracking

+-------------------------------------------------------------------------------------------+
| Test cases on Postman, an app that allows you to construct requests and analyze responses |
+-------------------------------------------------------------------------------------------+
- Test GET:
    URL: http://localhost:8000/proxy/http://httpbin.org/get
    Result (Status: 200 OK, Time: 416 ms):
    {
      "args": {},
      "headers": {
        "Accept-Encoding": "identity",
        "Host": "httpbin.org",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
      },
      "origin": "104.244.197.146",
      "url": "http://httpbin.org/get"
    }

- Test POST:
    URL: http://localhost:8000/proxy/http://httpbin.org/post
    Data: asdf=blah
    Result (Status: 200 OK, Time: 391 ms):
    {
      "args": {},
      "data": "",
      "files": {},
      "form": {
        "asdf": "blah"
      },
      "headers": {
        "Accept-Encoding": "identity",
        "Content-Length": "9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "httpbin.org",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
      },
      "json": null,
      "origin": "104.244.197.146",
      "url": "http://httpbin.org/post"
    }

"""

# Import useful libraries
import urllib.request
import urllib.parse
import socket
import _thread
import threading
import sys
import os


# Declare constants
hostname = "localhost"
port = 8000
address = (hostname, port)
MAX_QUEUE_LENGTH = 42
MAX_BUFFER_SIZE = 4096


# Debugging flag
DEBUG = 0
# Will display the following:
# - Unmodified HTTP request
# - Parsed HTTP method and URL
# - Parsed user-agent header
# - Request body (if a POST request)
# - Key-value pairs parsed from the request body (if a POST request)


def main():
    """Initializes and runs a web service that acts as an HTTP proxy.

    Using localhost:8000 as an example, the input format this server expects from clients is
    http://localhost:8000/proxy/<URL>, where <URL> is of the form "http://HOSTNAME"
    """
    # Create a socket and bind it to the specified address
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(address)
    server_sock.listen(MAX_QUEUE_LENGTH)

    try:
        # Start the server
        print("SERVER: Started on {0}:{1}. Enter URL in format http://{0}:{1}/proxy/URL".format(hostname, port))
        while True:
            # Produce dynamic client sockets
            conn, addr = server_sock.accept()
            _thread.start_new_thread(proxy, (conn,))
        server_sock.close()
    except KeyboardInterrupt:
        # Terminate the server with Control-C (use Control-Break/Control-Pause for best results)
        server_sock.close()
        print("SERVER: User requested an interrupt. Server closed")
        sys.exit(0)


def proxy(conn):
    """Serves a client request to a remote server, and returns the response of the remote server to the client.

    Args:
        conn: a socket object of the client being served

    Returns:
        response: result of the client's request to the remote server
    """
    # Receive data as raw bytes and decode it into a string
    request = conn.recv(MAX_BUFFER_SIZE).decode("UTF-8")
    print("SERVER: Client request received")

    if DEBUG:
        print(request)

    # Get the HTTP request line, then the method and url from the headers (could use urllib.parse next time)
    url = ""
    request_lines = request.split("\n")
    try:
        method = request_lines[0].split(" ")[0].upper()
        url = request_lines[0].split(" ")[1]

        if DEBUG:
            print("Method: " + method + ", URL: " + url)

        if url.find("/proxy/") != -1:
            url = url[url.find("/proxy/") + len("/proxy/"):]
        else:
            print("SERVER: Please specify a URL after {0}:{1}/proxy/ (received {2} instead)".format(hostname, port, url))
            conn.close()
            return None
    except (IndexError, StopIteration):
        pass

    # Search for the user-agent header in the HTTP request and remove trailing whitespace
    ua_header = ""
    try:
        ua_header = next(line for line in request_lines if "User-Agent" in line)[len("User-Agent") + 2:].rstrip()
    except StopIteration:
        pass

    if DEBUG:
        print("User-Agent: " + ua_header)

    headers = {"User-Agent": ua_header}

    # Serve the client's request
    try:
        if method == "GET":
            # Serves a GET request
            req = urllib.request.Request(url, data=None, headers=headers)
            response = urllib.request.urlopen(req).read()
            conn.sendall(response)
            print("SERVER: Client GET request served")
        elif method == "POST":
            # Serves a POST request

            # Locate the request body
            try:
                body_index = -1
                for line in request_lines:
                    if line in os.linesep:
                        body_index = request_lines.index(line)
                        break
                req_body = "".join(request_lines[body_index:]).strip()

                if DEBUG:
                    print("Request body: " + req_body)

                post_data = dict(item.split('=') for item in req_body.split('&'))

                if DEBUG:
                    for keys, values in post_data.items():
                        print("post_data: " + keys + ": " + values)

                # Encode the key-value pairs; first URL encode, then byte encode using UTF-8
                post_data = urllib.parse.urlencode(post_data)
                post_data = post_data.encode("UTF-8")

            except IndexError as e:
                print(e)
                print("SERVER: Client request not served")
                conn.close()
                return None

            req = urllib.request.Request(url, data=post_data, headers=headers)
            response = urllib.request.urlopen(req).read()
            conn.sendall(response)
            print("SERVER: Client POST request served.")
        else:
            print("SERVER: Request type unimplemented. Please try GET or POST")
        conn.close()
    except (ValueError, urllib.error.HTTPError) as e:
        print(e)
        print("SERVER: Client request not served")
        conn.close()
        return None

if __name__ == "__main__":
    main()
