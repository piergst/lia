# How to use a session cookie for an HTTP request with curl ? #script
```bash
URL="http://url.com"
COOKIE_FILE="cookie.txt"
HTML_CONTENT=$(curl -c "$COOKIE_FILE" -s "$URL")
$DATA="bar
RESPONSE=$(curl -s -b "$COOKIE_FILE" -d "foo=$DATA" -X POST "$URL")
echo "$RESPONSE"
rm -r "$COOKIE_FILE"
```
