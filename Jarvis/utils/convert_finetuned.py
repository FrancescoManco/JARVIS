import os
import subprocess


def convert_to_gguf(model_path, output_path):
    """
    Converte il modello fine-tunato in formato GGUF per Ollama.
    """
    gguf_model_path = os.path.join(output_path, "model.gguf")

    # Usa llama.cpp per convertire il modello
    conversion_command = [
        "python", "-m", "llama_cpp.convert_model",
        "--input", model_path,
        "--output", gguf_model_path
    ]
    try:
        subprocess.run(conversion_command, check=True)
        print(f"Modello convertito con successo e salvato in {gguf_model_path}")
        return gguf_model_path
    except subprocess.CalledProcessError as e:
        print(f"Errore nella conversione: {e}")
        return None


def create_modelfile(model_name, gguf_model_path):
    """
    Crea un Modelfile per Ollama.
    """
    modelfile_content = f"""
    FROM {gguf_model_path}

    SYSTEM: |
      Sei un assistente AI avanzato.

    TEMPERATURE: 0.7
    """

    modelfile_path = os.path.join(os.path.dirname(gguf_model_path), "Modelfile")

    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)

    print(f"Modelfile creato: {modelfile_path}")
    return modelfile_path


def import_into_ollama(model_name, modelfile_path):
    """
    Importa il modello in Ollama.
    """
    try:
        subprocess.run(["ollama", "create", model_name, "-f", modelfile_path], check=True)
        print(f"Modello {model_name} importato con successo in Ollama!")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'importazione in Ollama: {e}")


def load_finetuned_model_into_ollama(finetuned_model_path, model_name):
    """
    Converti, crea il Modelfile e importa il modello in Ollama.
    """
    output_path = os.path.dirname(finetuned_model_path)

    # Step 1: Converti in GGUF
    gguf_model_path = convert_to_gguf(finetuned_model_path, output_path)

    if gguf_model_path:
        # Step 2: Crea Modelfile
        modelfile_path = create_modelfile(model_name, gguf_model_path)

        # Step 3: Importa in Ollama
        import_into_ollama(model_name, modelfile_path)


