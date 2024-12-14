# EECS 4764 Final Project - Marco Polo



## Setup ESP8266

Instructions to flash ESP8266 with micropython
```
esptool.py erase_flash
esptool.py --baud 460800 write_flash --flash_size=detect 0 [FILE]
```

Uploading code to ESP

```
cd Final_Project
mpfshell -nc "open <PORT>; mput .*\.py"

```

## Run the webserver

You will need to modify the some global variables in 
`webapp.py` and `main.py` to make sure that the ESP and webapp can connect to each other on your network and use GPT-mini

```
cd Final_Project
pip install -r requirements.txt
python webapp/webapp.py
```
Start using!

## Examples

Sample gradio default webapp interface

![alt text](<Final_Project/images/Screenshot0.png>)

Asking to label an item
![alt text](<Final_Project/images/Screenshot1.png>)

Asking to read an item label
![alt text](<Final_Project/images/Screenshot2.png>)

Corresponding ESP repl for this interaction
![alt text](<Final_Project/images/Screenshot3.png>)

