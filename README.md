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
mpfshell -nc "open <PORT>; mput [FILES]"
```