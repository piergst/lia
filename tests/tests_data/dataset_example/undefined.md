# How to retrieve my public IP? #command
```bash
curl -4 ifconfig.me #ipv4
curl -6 ifconfig.me #ipv6
```
- Using a browser:
    - Go [here](https://ifconfig.me/) for IPv6
    - Go [here](https://whatismyipaddress.com/) for both IPv4 and IPv6

# How to enumerate directories on a website? #command
```bash
gobuster dir --no-error -u http://<targetip> -w /path/to/wordlist.txt
```

- **`dir`**: search for subdirectories of the domain
- **`--no-error`**: suppress access error logging
- **`-u`**: target URL
- **`-w`**: wordlist path

# How to create a minimal local HTTP server? #command
```python
python3 -m http.server 8000
```