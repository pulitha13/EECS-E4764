## Flashing ESP8266

```
esptool.py erase_flash
esptool.py --baud 460800 write_flash --flash_size=detect 0 [FILE]
```

## Using the repl shell
```
mpfshell --open <PORT> -nc repl
```


## Uploading code to flash

```
# General
mpfshell -nc "open <PORT>; mput [FILES]"

# To download ALL python files in your current dir 
mpfshell -nc "open <PORT>; mput .*\.py"

```

Example of how to send JSON command using bash

```
echo -n '{"cmd": "display_time", "args": []}' | nc 10.206.92.248 7000
```