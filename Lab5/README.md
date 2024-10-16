
## Send JSON to device

Make sure you are using the correct ip, port

```
echo -n '{"cmd": "screen_on", "args": []}' | nc 10.206.51.0 7000
```