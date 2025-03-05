# Funzioni di supporto
def credentials_to_dict(credentials):
    """Converte le credenziali in un dizionario"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def credentials_from_dict(credentials_info):
    """Restituisce un oggetto Credentials"""
    from google.oauth2.credentials import Credentials
    return Credentials(
        token=credentials_info['token'],
        refresh_token=credentials_info['refresh_token'],
        token_uri=credentials_info['token_uri'],
        client_id=credentials_info['client_id'],
        client_secret=credentials_info['client_secret'],
        scopes=credentials_info['scopes']
    )
