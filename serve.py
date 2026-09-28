"""Serve the viewer locally.

    python serve.py                 # http://127.0.0.1:8000
    python serve.py --port 9000 --no-browser

Binds to localhost only. HoliSafe's terms require restricting access to
authorised people, so do not expose this on a public interface.
"""
import argparse
import functools
import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if not self.path.startswith("/img/"):
            super().log_message(fmt, *args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    if not any(os.path.exists(os.path.join(SITE, f)) for f in ("vlsbench.json", "holisafe.json")):
        sys.exit("No data built yet. Run: python download.py && python build.py")
    url = f"http://127.0.0.1:{a.port}/"
    httpd = ThreadingHTTPServer(("127.0.0.1", a.port), functools.partial(Handler, directory=SITE))
    print(f"Viewer running at {url}  (Ctrl-C to stop)")
    if not a.no_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
