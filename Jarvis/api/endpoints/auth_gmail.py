
import os
import uuid

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

from Jarvis.api.endpoints.utils.credentials import credentials_to_dict

# Disabilita il controllo HTTPS solo per ambiente di sviluppo locale
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configurazioni
CLIENT_SECRETS_FILE = r"D:\Jarvis\jarvis\core\objective\moduls\e-mail\credentials.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = "http://localhost:8000/callback"

router = APIRouter()

# Salva i flussi e i token
oauth_flows = {}

device_id = str(uuid.uuid4())
@router.get("/")
async def main():
    return {"message": "Visita /authorize per autorizzare l'accesso alle tue email."}


@router.get("/authorize")
async def authorize(request: Request):
    # Crea il flusso di autorizzazione
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    # Salva il flusso per usarlo dopo
    oauth_flows[request.client.host] = flow

    # Ottieni l'URL di autorizzazione
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    return RedirectResponse(url=authorization_url)


@router.get("/callback")
async def callback(request: Request):
    flow = oauth_flows.get(request.client.host)
    if not flow:
        return {"error": "Autenticazione non trovata."}


    # Completa il flusso OAuth 2.0
    flow.fetch_token(authorization_response=str(request.url))

    credentials = flow.credentials

    # Salva i credenziali in un file o memoria (per sessioni future)
    with open(f'credentials_{device_id}.json', 'w') as token:
        json.dump(credentials_to_dict(credentials), token)


    return {"message": "Autenticazione completata, ora puoi ottenere le tue email."}







