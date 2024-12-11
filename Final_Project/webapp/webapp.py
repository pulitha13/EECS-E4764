import gradio as gr
import whisper
import asyncio
import fastapi_poe as fp
import socket
import json
from gtts import gTTS
import os
import requests

POE_API_KEY = ''
IP = '10.206.111.21'
CMD_PORT = 7000
CMD_LIT_PORT = 7001
prompt_header = """

You are a voice assistant for a blind human being. They are either telling you about a label that they want to write on some object or asking
to you to read data about that object. You will interpret what the user says and translate it into a JSON object (no markdown) that is less than
256 bytes long one of the following ways:


- If the user is asking a question or seeking information or saying something along the lines of "read this"

{"payload": {} , "command": "read"}

- If the user is making a request or giving an instruction

{"payload": {"name": Object_name, "time": timestamp, "location": loc} , "command": "write"}

- If the user's words are not parseable into the above two cases
{"payload": {}, "command": "error"}

The `Object_name` should be inferred from the user's words, and the `timestamp` should be the UTC time at which the message was recorded.
Here, the timestamp variable is the UTC time at which the message was recorded. `loc` should be inferred if the user mentions a location 
that the object is being written to, however, if there is no location that can be inferred by the user just set `loc` to an empty string.

This is the user's command: 

"""

async def get_llm_response(prompt):

    full_prompt = prompt_header + prompt

    message = fp.ProtocolMessage(role="user", content=full_prompt)
    full_response = ""
    async for partial in fp.get_bot_response(messages=[message], 
                        bot_name='GPT-4o-Mini', 
                        api_key=POE_API_KEY):
        full_response += partial.text
    return full_response


def send_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        esp_address = (IP, CMD_PORT)  # Example server and port
        sock.connect(esp_address)
        print(command)
        json.loads(command)
        sock.sendall(command.encode('utf-8'))
        print("Sent: ", command)

    except Exception as e:
        print(f"send_command: error: {e}")

    return read_response(sock)

def read_response(s):
        
    try:
        #Receive the command (data sent by the client)
        data = s.recv(1024) #Max 1024 bytes

        if data:
            json_data = json.loads(data.decode('utf-8'))
            if(json_data['status'] == "success"):
                return generate_legible_response(json_data['message'])
            return "fail"
        else:
            print("No data received")
            return None

    except Exception as e:
        print(f"Error: {e}")

    finally:
        s.close()

def generate_legible_response(json):

    if(isinstance(json, str)):
        return json

    string = ""
    if "name" in json:
        string += "This is a " + json["name"]
    
    if "location" in json and json['location']:
        string += " that you stored in " + json['location']

    return string

def process_input(audio):

    whisper_model = whisper.load_model("tiny.en")
    whisp_transcription = whisper_model.transcribe(audio)["text"]
    llm_resp = asyncio.run(get_llm_response(prompt_header+whisp_transcription))
    print("llm_resp", llm_resp)
    try:
        response = send_command(llm_resp)
    except Exception as e:
        print(f'process_input: error: {e}')
    audio_file = convert_text_to_speech(response)
    transcription = f"Transcribed response: {whisp_transcription}"
    llm_response = f"JSON interpretation: {llm_resp}"
    cardreader_response = f"Card Reader response: {response}"

    return transcription, llm_response, cardreader_response, audio_file

ui = gr.Interface(
    inputs=[ gr.Audio(sources=["microphone"], type="filepath", label="Voice Input"),],
        fn=process_input,
        outputs=[
        gr.Textbox(label="Transcription/Input"),
        gr.Textbox(label="LLM Response"),
        gr.Textbox(label="Smartwatch Response"),
        gr.Audio(label="Audio Response")
        ],
        title="Voice Assistant",
        description="My capabilities: Help the visually impaired store and manage their goods.",
        allow_flagging="never"
        )

################################### Audio Processing for response #####################################################

def convert_text_to_speech(text):
    try:
        tts = gTTS(text, lang='en')
        audio_file = "response.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    ui.launch(debug=False, share=True)

