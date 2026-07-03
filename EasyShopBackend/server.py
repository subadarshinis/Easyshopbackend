from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import psycopg2

# PostgreSQL Connection
conn = psycopg2.connect(
    host="localhost",
    database="SUBA-Python",
    port=5432,
    user="SubadarshiniS",
    password="SuB@2oo7"
)

logged_in_users = set()

# ---------------- Users Class ----------------



# ---------------- HTTP Handler ----------------
class RequestHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
        except:
            self.send_json(400, {"message": "Invalid JSON"})
            return

        cursor = conn.cursor()

        # -------- Signup --------
        if self.path == "/signup":
            if "username" not in data or "password" not in data:
                self.send_json(400, {"message": "username and password required"})
                return
            username = data["username"]
            password = data["password"]

            cursor.execute(
                "SELECT 1 FROM authdb.users WHERE username=%s",
                (username,)
            )

            if cursor.fetchone():
                self.send_json(400, {"message": "User already exists"})
                return

            cursor.execute(
                "INSERT INTO authdb.users(username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()

            self.send_json(200, {"message": "Signup successful"})

        # -------- Login --------
        elif self.path == "/login":
            if "username" not in data or "password" not in data:
                self.send_json(400, {"message": "username and password required"})
                return

            username = data["username"]
            password = data["password"]

            cursor.execute(
                "SELECT 1 FROM authdb.users WHERE username=%s AND password=%s",
                (username, password)
            )

            if cursor.fetchone():
                logged_in_users.add(username)
                self.send_json(200, {"message": "Login successful"})
            else:
                self.send_json(401, {"message": "Invalid username or password"})

        # -------- Logout --------
        elif self.path == "/logout":
            username = data.get("username")

            if username in logged_in_users:
                logged_in_users.remove(username)
                self.send_json(200, {"message": "Logout successful"})
            else:
                self.send_json(400, {"message": "User is not logged in"})

        else:
            self.send_json(404, {"message": "API Not Found"})


# ---------------- Server Start ----------------
server = HTTPServer(("localhost", 8080), RequestHandler)
print("Server started on http://localhost:8080")
server.serve_forever()