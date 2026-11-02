#!/usr/bin/env python3
"""Serve the built web edition locally the way Azure Static Web Apps serves it.

    python3 tools/serve.py [dist/site] [--port 8080]

Reads dist/site/staticwebapp.config.json and applies what a static book needs from it: globalHeaders
(the CSP and the other security headers), routes (exact and trailing-* routes, first match wins:
"rewrite" and per-route "headers", such as the Link headers and the .well-known rewrites the build
generates), mimeTypes and the 404 override. Good enough to test the site with Lighthouse, an agent
or a browser on http://localhost (a secure context, so WebMCP works there). It is not the real
Static Web Apps runtime: no auth, no redirects, no navigationFallback, no API.
"""
import argparse, functools, http.server, json, mimetypes, pathlib, posixpath, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent

def load(site):
    p = site / "staticwebapp.config.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def match(route, path):
    if route.endswith("*"):
        return path.startswith(route[:-1])
    return path == route

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, site=None, cfg=None, **kw):
        self.site, self.cfg = site, cfg
        super().__init__(*a, directory=str(site), **kw)

    def _route(self, path):
        for r in self.cfg.get("routes", []):
            if match(r.get("route", ""), path):
                return r
        return None

    def send_head(self):
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        r = self._route(path)
        self._extra = dict(self.cfg.get("globalHeaders", {}))
        if r:
            self._extra.update(r.get("headers", {}))
            if r.get("rewrite"):
                self.path = r["rewrite"]
        fs = pathlib.Path(self.translate_path(self.path))
        if fs.is_dir():
            fs = fs / "index.html"
        if not fs.is_file():
            nf = self.cfg.get("responseOverrides", {}).get("404", {}).get("rewrite")
            if nf and (self.site / nf.lstrip("/")).is_file():
                body = (self.site / nf.lstrip("/")).read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                return __import__("io").BytesIO(body)
            self.send_error(404)
            return None
        self.path = "/" + fs.relative_to(self.site).as_posix()
        return super().send_head()

    def guess_type(self, path):
        ext = posixpath.splitext(str(path))[1].lower()
        mt = self.cfg.get("mimeTypes", {})
        return mt.get(ext) or mimetypes.guess_type(str(path))[0] or "application/octet-stream"

    def end_headers(self):
        for k, v in getattr(self, "_extra", {}).items():
            if k.lower() == "content-type":
                continue
            self.send_header(k, v)
        super().end_headers()

    def send_header(self, k, v):
        if k.lower() == "content-type":
            ct = getattr(self, "_extra", {}).get("Content-Type")
            if ct:
                v = ct
        super().send_header(k, v)

    def log_message(self, fmt, *args):
        pass

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("site", nargs="?", default=str(ROOT / "dist" / "site"))
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args(argv)
    site = pathlib.Path(a.site).resolve()
    cfg = load(site)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), functools.partial(Handler, site=site, cfg=cfg))
    print(f"serving {site} on http://localhost:{a.port}/ (Ctrl+C to stop)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
