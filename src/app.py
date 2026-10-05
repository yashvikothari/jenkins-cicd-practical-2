import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

APP_NAME = os.getenv("APP_NAME", "Jenkins CI/CD Demo")
APP_ENV = os.getenv("APP_ENV", "swarm")
APP_VERSION = os.getenv("APP_VERSION", "dev")
PORT = int(os.getenv("PORT", "8080"))

def health_payload():
    return {
        "status": "ok",
        "app": APP_NAME,
        "environment": APP_ENV,
        "version": APP_VERSION,
    }

def home_html():
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{APP_NAME}</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: Arial, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
    }}
    .card {{
      width: min(720px, 88vw);
      padding: 42px;
      border: 1px solid #334155;
      border-radius: 20px;
      background: #111827;
      box-shadow: 0 22px 60px rgba(0,0,0,.35);
    }}
    .badge {{
      display: inline-block;
      padding: 7px 12px;
      border-radius: 999px;
      background: #14532d;
      color: #bbf7d0;
      font-weight: 700;
    }}
    h1 {{ font-size: 42px; margin: 20px 0 8px; }}
    .version {{ font-size: 26px; font-weight: 700; color: #93c5fd; }}
    .meta {{ margin-top: 26px; color: #94a3b8; line-height: 1.8; }}
    code {{ color: #f8fafc; }}
  </style>
</head>
<body>
  <main class="card">
    <span class="badge">APPLICATION HEALTHY</span>
    <h1>{APP_NAME}</h1>
    <div class="version">Version: {APP_VERSION}</div>
    <div class="meta">
      Environment: <code>{APP_ENV}</code><br>
      Health endpoint: <code>/health</code><br>
      Deployment: <code>Docker Swarm rolling update</code>
    </div>
  </main>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps(health_payload()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
        else:
            body = home_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")

        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{APP_NAME} {APP_VERSION} listening on port {PORT}", flush=True)
    server.serve_forever()
