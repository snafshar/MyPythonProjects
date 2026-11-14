# Universal Server Demo (Python)

Five beginner-friendly servers, written using only the Python standard library (Python 3.10+).

| Service | Port | Description |
|---|---:|---|
| File | 8001 | Upload/download with a token (10 MB maximum) |
| API | 8002 | GET /api/hello |
| Proxy | 8003 | Fixed reverse proxy to the API |
| Monitoring | 8004 | GET /metrics, requires token |
| Mail | 1025 | Test SMTP inbox, stores received mail locally |

## Run

```bash
export SERVER_TOKEN='replace-with-a-long-secret'
python3 main.py
```

Open another terminal:

```bash
# API
curl http://127.0.0.1:8002/api/hello

# Same API via fixed reverse proxy
curl http://127.0.0.1:8003/api/hello

# Upload and download
printf 'Hello!\n' > hello.txt
curl -X POST -H "X-Token: $SERVER_TOKEN" --data-binary @hello.txt http://127.0.0.1:8001/files/hello.txt
curl -H "X-Token: $SERVER_TOKEN" http://127.0.0.1:8001/files/hello.txt -o downloaded.txt

# Request counts
curl -H "X-Token: $SERVER_TOKEN" http://127.0.0.1:8004/metrics
```

Send a test email (it is only saved in `received_mail/`):

```python
import smtplib
from email.message import EmailMessage

message = EmailMessage()
message["From"] = "alice@example.test"
message["To"] = "bob@example.test"
message["Subject"] = "Hello"
message.set_content("This is a local test email.")

with smtplib.SMTP("127.0.0.1", 1025) as smtp:
    smtp.send_message(message)
```

## Send a file on the LAN

On the receiving computer, start:

```bash
export SERVER_TOKEN='a-long-secret'
python3 main.py --host 0.0.0.0
```

On a second computer (replace IP and token):

```bash
curl -X POST -H 'X-Token: a-long-secret' --data-binary @photo.jpg http://192.168.1.20:8001/files/photo.jpg
```

Allow incoming TCP 8001 in the receiving machine's firewall. Only file and proxy ports are exposed by `--host`; the API, mail, and monitoring services stay on localhost.

## Important limitations

This is **educational code, not production-ready software**. The file transfer uses plain HTTP and exposes both the secret token and file content to network observers. Use only on a trusted LAN; choose SFTP/SSH or HTTPS for sensitive files. File names are restricted to a single path component, but authorized uploads can replace existing files. The SMTP service accepts limited commands and **never relays or delivers internet mail**. The proxy only forwards `/api/hello` to a fixed internal destination; it is not an open proxy. Monitoring reports in-memory request counts, not CPU/RAM or uptime. No external dependencies, database, TLS, rate limiting, or persistence of metrics are included.

Run tests with `python3 -m unittest discover -s tests -v`.
