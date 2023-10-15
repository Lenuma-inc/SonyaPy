import voice
import sounddevice as sd
import vosk
import json
import queue
import threading

voice.bot_speak("Соня вас внимательно слушает ...")

messages = [
    {"role": "system", "content": "Ты голосовой ассистент по имени Соня."}
]
q = queue.Queue()

model = vosk.Model("model_small_ru")

device = sd.default.device  # <--- по умолчанию
samplerate = int(
    sd.query_devices(device[0], "input")["default_samplerate"]
)  # получаем частоту микрофона


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def main():
    # постоянная прослушка микрофона
    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=16000,
        device=device[0],
        dtype="int16",
        channels=1,
        callback=callback,
    ):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())["text"]
                recognize(data)
                clear_text(data)


def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages


# преобразование текста в речь
def recognize(data):
    print("Пользователь сказал: " + data)
    if data.startswith("соня"):
        # обращаются к ассистенту
        text = clear_text(data)
        print("Сервер получил: " + text)
        update_chat(messages, "user", text)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response = completion.choices[0].message.content
        if response != None:
            answer = response.lower()
            print("Сервер ответил: " + answer)
            voice.bot_speak(answer)
        else:
            voice.bot_speak("Сервер ничего не ответил")

# очистка текста от имени бота
def clear_text(data):
    text = data
    text = text.replace('соня', '').strip()
    text = text.replace('  ', ' ').strip()
    return text


def start_thread():
    my_thread = threading.Thread(target=main, args=())
    my_thread.start()


while True:
    start_thread()
