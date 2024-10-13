
## Send JSON to device

Make sure you are using the correct ip, port

```
echo -n '{"cmd": "screen_on", "args": []}' | nc 192.168.1.81 7000
```