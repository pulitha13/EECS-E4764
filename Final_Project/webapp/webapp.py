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
IP = '10.206.150.248'
CMD_PORT = 7000
CMD_LIT_PORT = 7001
prompt_header = """

You are a voice assistant for a blind human being. They are telling you information that they want to write down on a very 
very  short note paper. These messages should be condensable to about 256 characters. You will interpret this message in a 
JSON object (no markdown) with a timestamp in the following way:

{"name":Object_name, "time": timestamp, "payload": message}

- If the user is asking a question or seeking information, set the `payload` to "read."
- If the user is making a request or giving an instruction, set the `payload` to "write."
- The `Object_name` should be inferred from the user's command, and the `timestamp` should be the UTC time at which the message was recorded.

Here, the timestamp variable is the UTC time at which the message was recorded, and the message variable is the shortened message 
that the user said.

This is the user's command: 
"""

# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
                message = json_data['name']
                print(f"Received message, the scanned item is: {message}")
                return message
            else:
                print("No data received")
                return None

        except Exception as e:
            print(f"Error: {e}")

        finally:
            s.close()
    
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

