import gradio as gr
import whisper
def process_input(audio):

	whisper_model = whisper.load_model("tiny.en")
	llm_resp = whisper_model.transcribe(audio)["text"]
	transcription = f"Placeholder for audio: {audio}"
	llm_response = f"Transcribed response: {llm_resp}"
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

