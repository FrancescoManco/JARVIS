import base64
import re
from Jarvis.api.endpoints.utils.credentials import credentials_from_dict
from Jarvis.subjective.finetuning.tuning import train_on_dataset
from Jarvis.utils.Ollama import llama
from Jarvis.utils.prompt import prompt_email_generation, prompt_email_generation_non_preferred
import os
import json
import datetime
import pandas as pd
from googleapiclient.discovery import build


# Funzione per estrarre il corpo dell'email
def get_email_body(payload):
    """Estrae il corpo del messaggio da una risposta dell'API Gmail"""
    body = None
    if 'body' in payload:

        body = payload['body'].get('data')
    elif 'parts' in payload:
        # Gestione delle email che contengono più parti (HTML, testo, etc.)
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body'].get('data')
            elif part['mimeType'] == 'text/html':
                body = part['body'].get('data')

    if body:
        # Gmail API codifica il corpo in base64url, quindi va decodificato
        return base64.urlsafe_b64decode(body).decode("utf-8")
    return None
def decode_base64_string(body):
    try:
        # Aggiungi padding se necessario
        padding = '=' * (-len(body) % 4)
        body += padding

        # Usa urlsafe_b64decode per decodificare i dati che sono stati codificati con urlsafe Base64
        print( base64.urlsafe_b64decode(body).decode('utf-8'))
        return base64.urlsafe_b64decode(body).decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"Errore nella decodifica: {e}")
        return None
def remove_urls(text):
    # Regex per trovare e rimuovere URL
    url_pattern = r'http[s]?://\S+|www\.\S+'
    cleaned_text = re.sub(url_pattern, '', text)
    return cleaned_text

# Funzione per ottenere le email inviate
def get_emails():
    print("genero_email")
    credentials_path = f'D:/Jarvis/credentials_1.json'
    if not os.path.exists(credentials_path):
        print("Autenticazione dispositivo non effettuata")
        return {"error": "Autenticazione richiesta."}

    with open(credentials_path, 'r') as token:
        credentials_info = json.load(token)

    credentials = credentials_from_dict(credentials_info)

    # Recupera le email inviate tramite Gmail API
    service = build('gmail', 'v1', credentials=credentials)

    # Aggiungi il filtro per le email inviate
    results = service.users().messages().list(userId='me', labelIds=['SENT'], maxResults=10).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:


        message = service.users().messages().get(userId='me', id=msg['id']).execute()

        # Estrai le parti dell'email
        message= message.get('payload', {}).get('parts', [])

        for part in message:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                decoded_data = decode_base64_string(body)
                cleaned_data = remove_urls(decoded_data)  # Rimuove gli URL
                emails.append(cleaned_data)
    # Dopo aver recuperato tutte le email inviate, chiama la funzione di generazione
    if len(emails) > 0:
        email_generation(emails)
    return {"emails": emails}


# Funzione di generazione email
def email_generation(list_email):
    email_results = []
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        while len(email_results) < 160:
            for email in list_email:
                prompt = prompt_email_generation(email)
                syntetic_email = llama(prompt)
                prompt_non_prefered=prompt_email_generation_non_preferred(email)
                email_non_preferita = llama(prompt_non_prefered)
                email_results.append({'prompt': email, 'chosen': syntetic_email,'rejected': email_non_preferita})

        # Salva le email generate in un file Excel
        df = pd.DataFrame(email_results)
        df.to_excel(f"email_generated/emails_{today_date}.xlsx", index=False)
        train_on_dataset(f"email_generated/emails_{today_date}.xlsx")
        return True
    except Exception as e:
        print(f"Errore nella generazione delle email: {e}")
        return False


