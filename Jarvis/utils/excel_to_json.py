import os
import pandas as pd
import json

def excel_to_json(folder_path):
    """
    Convert all Excel files in a folder to JSON files with the same name.

    Args:
        folder_path (str): Path to the folder containing Excel files.
    """
    # Verifica che la cartella esista
    if not os.path.exists(folder_path):
        print(f"La cartella '{folder_path}' non esiste.")
        return

    # Ottieni tutti i file nella cartella
    files = os.listdir(folder_path)

    # Filtra solo i file Excel
    excel_files = [f for f in files if f.endswith('.xlsx') or f.endswith('.xls')]

    if not excel_files:
        print("Nessun file Excel trovato nella cartella.")
        return

    for excel_file in excel_files:
        excel_path = os.path.join(folder_path, excel_file)
        json_path = os.path.join(folder_path, os.path.splitext(excel_file)[0] + '.json')

        try:
            # Leggi il file Excel
            df = pd.read_excel(excel_path)

            # Converti il DataFrame in dizionario
            data_dict = df.to_dict(orient='records')

            # Scrivi i dati in un file JSON
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

            print(f"Creato file JSON: {json_path}")
        except Exception as e:
            print(f"Errore durante la conversione di '{excel_file}': {e}")

