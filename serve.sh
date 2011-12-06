{ echo -ne "HTTP/1.0 200 OK\r\n\r\n"; cat ~/src/charlotte/serve.file; } | nc -l 80 &
