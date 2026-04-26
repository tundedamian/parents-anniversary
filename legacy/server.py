import http.server
import socketserver
import json
import os
import datetime

PORT = 8000
COMMENTS_FILE = "comments.json"

if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        json.dump([], f)

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/comments':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            with open(COMMENTS_FILE, 'r') as f:
                content = f.read()
                if not content:
                    content = "[]"
                self.wfile.write(content.encode('utf-8'))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/comments':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                comment = json.loads(post_data.decode('utf-8'))
                comment['time'] = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
                
                with open(COMMENTS_FILE, 'r+') as f:
                    try:
                        comments = json.load(f)
                    except ValueError:
                        comments = []
                    comments.append(comment)
                    f.seek(0)
                    json.dump(comments, f)
                    f.truncate()
                    
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "comment": comment}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
            return
        self.send_response(404)
        self.end_headers()

Handler = MyHttpRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
