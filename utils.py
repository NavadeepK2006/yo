from PyPDF2 import PdfReader
from gtts import gTTS
def extract_text_from_pdf(file):
    reader=PdfReader(file)
    text=""
    for page in reader.pages:
        text+=page.extract_text()
    return text
def speak_text(text):
    tts=gTTS(text=text,lang='en')
    tts.save("tts_output.mp3")