import http.client
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main


class Tests(unittest.TestCase):
    def test_filename_validation(self):
        for path in ("/files/../bad", "/files/%2e%2e%2fsecret", "/files/", "/files/a%5cb"):
            self.assertIsNone(main.safe_filename(path))
        self.assertEqual(main.safe_filename("/files/hello.txt"), "hello.txt")

    def test_file_upload_and_api(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(main, "FILES", Path(tmp)):
            file_srv = ThreadingHTTPServer(("127.0.0.1", 0), main.FileServer)
            api_srv = ThreadingHTTPServer(("127.0.0.1", 0), main.APIServer)
            for srv in (file_srv, api_srv):
                threading.Thread(target=srv.serve_forever, daemon=True).start()
            try:
                c = http.client.HTTPConnection("127.0.0.1", file_srv.server_port)
                c.request("POST", "/files/demo.txt", b"hello", {"X-Token": main.TOKEN})
                r = c.getresponse()
                self.assertEqual(r.status, 201)
                r.read()
                c.request("GET", "/files/demo.txt", headers={"X-Token": main.TOKEN})
                self.assertEqual(c.getresponse().read(), b"hello")
                c.close()
                c = http.client.HTTPConnection("127.0.0.1", api_srv.server_port)
                c.request("GET", "/api/hello")
                self.assertIn(b"Hello", c.getresponse().read())
                c.close()
            finally:
                for srv in (file_srv, api_srv):
                    srv.shutdown()
                    srv.server_close()


if __name__ == "__main__":
    unittest.main()
