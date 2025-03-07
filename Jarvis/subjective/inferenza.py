import os

import torch

from unsloth import FastLanguageModel







def generate_response(model, tokenizer, prompt, max_length=2048):
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_length)
    inputs = {key: value.to(model.device) for key, value in inputs.items()}  # Porta i dati sul dispositivo corretto
    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            num_beams=1,  # Cambia questo valore se non vuoi usare beam search
            early_stopping=True,
        )
    return tokenizer.decode(outputs[-1], skip_special_tokens=True)



def fine_tuned_response(prompt, max_length=2048):
    #print(prompt)
    # Ottieni il percorso della cartella corrente (dove si trova lo script)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Costruisci il percorso della cartella modello (finetuning/model)
    model_dir = os.path.join(base_dir, "finetuning", "model")

    # Controlla se la cartella modello esiste
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"The Folder doesn't exist: {model_dir}")

    # Trova la prima sottocartella dentro 'model'
    subdirectories = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]

    if not subdirectories:
        raise ValueError("Any subfolder in the  directory of the model.")

    fine_tuned_model_path = os.path.join(model_dir, subdirectories[0])

    # Carica il modello e il tokenizer
    fine_tuned_model, fine_tuned_tokenizer = FastLanguageModel.from_pretrained(
        model_name=fine_tuned_model_path,
        max_seq_length=1024,
        dtype=None,
        load_in_4bit=False,
        use_exact_model_name=True,
    )

    # **CORREZIONE**: Prepara il modello per l'inferenza con Unsloth
    FastLanguageModel.for_inference(fine_tuned_model)

    try:
        risp = generate_response(
            fine_tuned_model, fine_tuned_tokenizer, prompt, max_length=max_length
        )
        print(risp)
        return risp
    except Exception as e:
        print(f"Errore nella generazione della risposta: {e}")
        return None

