from openai import OpenAi
import shelve
from dotenv import load_dotenv
import os 
import time 
import logging 

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_KEY")
OPENAI_ASSISTANT_ID = os.getenv("ASSISTANT_KEY")
client = OpenAi(api_key=OPENAI_API_KEY)

def upload_file(path):
    file = client.files.create(
        file.open("../../data/airbnb-faq.pdf", "rb"), purpose = "assistants"
    )

def create_assistant(file): 
    assistant = client.beta.assistants.create(
        name = "whatsapp assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests that are staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools = [{"type": "retrieval"}],
        model = "gpt-4-1106-preview",
        file_ids=[file.id]
    )
    return assistant


def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)
    
def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

def run_assistant(thread, name):
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
    run = client.beta.threads.runs.create(
        thread_id = thread.id,
        assistant_id = assistant.id
    )

    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        #messages
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        new_message = messages.data[0].content[0].text.value
        logging.info(f"Generated message: {new_message}")
        return new_message


def generate_response(message_body, wa_id, name): 
    thread_id = check_if_thread_exists(wa_id)
    if thread_id in None:
        logging.info(f"crearing a new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread_id)
        thread_id = thread.id

    else: 
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

        message = client.beta.threads.message.create(
            thread_id = thread_id,
            role = "user",
            content=message.body
        )

    new_message = run_assistant(thread, name)

    return new_message
