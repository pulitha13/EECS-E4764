
## Send JSON to device

Make sure you are using the correct ip, port

(ESP IP is printed to terminal)

```
echo -n '{"cmd": "screen_on", "args": []}' | nc 10.206.51.0 7000
```

## Test Letter Stuff

1) Make sure the server is running. Use the EXTERNAL IP not the one printed by the script. You need to go to the cloud website ting for that
2) Flash the board w/ the code
3) do the following in terminal or do some equivalent for windows (basically sending the json command)

```
echo -n '{"cmd": "write_message", "args": []}' | nc 10.206.51.0 7000
```

