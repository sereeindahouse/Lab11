"""Vercel Python serverless функц:  GET /api/solve?map=m05_a&p=0.8&gamma=0.95&seed=42

A*, BFS, Value Iteration ба нэг оролдлогын үр дүнг JSON-оор буцаана (warehouse/web.py).
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from warehouse.web import BadRequest, parse_params, solve  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        q = dict(parse_qsl(urlparse(self.path).query))
        try:
            body, status = solve(*parse_params(q)), 200
        except BadRequest as e:
            body, status = {"error": str(e)}, 400
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if status == 200:
            # Үр дүн тодорхой (deterministic) тул CDN дээр нэг өдөр хадгална
            self.send_header("Cache-Control", "public, s-maxage=86400")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
