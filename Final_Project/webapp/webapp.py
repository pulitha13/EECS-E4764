import gradio as gr
import whisper
import asyncio
import fastapi_poe as fp
import socket
import json

POE_API_KEY = ''
IP = 'localhost'
CMD_PORT = 7000
prompt_header = """

You are a voice assistant for a blind human being. They are telling you information that they want to write down on a very 
very  short note paper. These messages should be condensable to about 256 characters. You will interpret this message in a 
JSON object with a timestamp in the following way:

{time: timestamp, payload: message}

Here, the timestamp variable is the UTC time at which the message was recorded, and the message variable is the shortened message 
that the user said.

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


	try:
			# Create a TCP/IP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		server_address = (IP, CMD_PORT)  # Example server and port
		sock.connect(server_address)

		json.loads(command)
		sock.sendall(command.encode('utf-8'))
		print("Sent: ", command)

	except Exception as e:
		print("error: {e}")

	finally:
		if sock:
			sock.close()



def process_input(audio):

	whisper_model = whisper.load_model("tiny.en")
	whisp_transcription = whisper_model.transcribe(audio)["text"]
	llm_resp = asyncio.run(get_llm_response(whisp_transcription))
	send_command(llm_resp)
	transcription = f"Transcribed response: {whisp_transcription}"
	llm_response = f"JSON interpretation: {llm_resp}"
	smartwatch_response = f"Placeholder for smartwatch response"
	return transcription, llm_response, smartwatch_response

ui = gr.Interface(
	inputs=[ gr.Audio(sources=["microphone"], type="filepath", label="Voice Input"),],
		fn=process_input,
		outputs=[
		gr.Textbox(label="Transcription/Input"),
		gr.Textbox(label="LLM Response"),
		gr.Textbox(label="Smartwatch Response")
		],
		title="Voice Assistant",
		description="My capabilities: XXX",
		allow_flagging="never"
		)

if __name__ == "__main__":



	ui.launch(debug=False, share=True)

	sock.close()

# if __name__ == "__main__":

# 	while (1):

# 		prompt = prompt_header

# 		prompt += input("Enter a prompt: ")
# 		print(asyncio.run(get_llm_response(prompt)))
