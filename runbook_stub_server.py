#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent


def load_json(name: str):
    with (BASE_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


class RunbookStubHandler(BaseHTTPRequestHandler):
    def _write_json(self, status_code: int, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/business-units/find":
            payload = load_json("find.json")
            name = query.get("name", [""])[0]
            if name:
                payload["requestedName"] = name
            self._write_json(200, payload)
            return

        if path == "/business-units/runbook-business-unit/profileinfo":
            self._write_json(200, load_json("profileinfo.json"))
            return

        if path == "/business-units/runbook-business-unit":
            self._write_json(200, load_json("reviewcount.json"))
            return

        if path == "/business-units/runbook-business-unit/reviews":
            page = query.get("page", ["1"])[0]
            filename = f"reviews-page-{page}.json"
            fixture = BASE_DIR / filename
            if fixture.exists():
                self._write_json(200, load_json(filename))
            else:
                self._write_json(404, {"error": f"missing fixture: {filename}"})
            return

        self._write_json(404, {"error": f"unsupported path: {path}"})

    def log_message(self, format, *args):
        return


def main():
    # Local-only version kept for reference:
    # server = HTTPServer(("127.0.0.1", 8089), RunbookStubHandler)
    # print("RUNBOOK stub server listening on http://127.0.0.1:8089")

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8089"))

    server = HTTPServer((host, port), RunbookStubHandler)
    print(f"RUNBOOK stub server listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
