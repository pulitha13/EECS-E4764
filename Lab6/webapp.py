import gradio as gr
import whisper
import asyncio
import fastapi_poe as fp
import socket
import json

POE_API_KEY = '2-j_yibA8pbfozuVugcd8qTYAC-4Iu4XHNEOtuEV5qE'
IP = '10.206.7.36'
CMD_PORT = 7000
prompt_header = """

You are a voice assistant for a smartwatch. Interprete the user's command and respond with
a JSON object (no markdown) that calls specific functions for the smartwatch. The available functions are:

- Turn on the screen : {cmd: screen_on, args:[]}
- Turn off the screen : {cmd: screen_off, args:[]}
- Displays the time on screen : {cmd: display_time, args:[]}
- Displays a message on screen (where message is a string) : {cmd: display_message, args:[message]}
- Writes a message on screen (where message is a string) : {cmd: write_message, args:[]}
- Sets an alarm for the watch (the arguements hour, minute, second are in military time) : {cmd: set_alarm, args:[hour, minute, second]}
- Displays the user's location on the screen : {cmd: display_location, args:[]}
- Displays the weather at user's location on the screen : {cmd: display_weather, args:[]}

You should understand the user's request or question and try your best to parse the request into one of the functions above
and return the corresponding JSON format. Assume that for the functions above, the watch has its own ability to calculate the
current location, current weather, set alarms, display short messages, and display times. Your job is to send commands to the 
watch based on the user input. 

Iterpret questions similar to "Where am I?" as a command to the watch to display the current location.

If and only if the request does not fit into any of the above functions answer the question based on your own knowledge and return the 
JSON corresponding to the "Display message" command and with your answer as the message arguement. Make sure your response is
under 48 characters.

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
