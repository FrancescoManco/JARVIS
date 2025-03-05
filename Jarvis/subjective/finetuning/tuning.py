import datetime
import os
from typing import List, Optional

import pandas as pd
import requests
import torch
from datasets import load_dataset, load_from_disk, DatasetDict, concatenate_datasets, Dataset
from datasets.exceptions import DatasetGenerationError
from unsloth import FastLanguageModel, apply_chat_template
from unsloth import PatchDPOTrainer

from transformers import TrainingArguments
from trl import DPOTrainer

from Jarvis.config import MODEL_BASE_PATH
from Jarvis.utils.convert_finetuned import load_finetuned_model_into_ollama

max_seq_length = 4096 # Choose any! We auto support RoPE Scaling internally!
dtype = None # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = False# Use 4bit quantization to reduce memory usage. Can be False.
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "0"





def model_(path_model):
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=path_model,
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit,
        use_exact_model_name=True
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=8,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=64,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
        use_rslora=False,
        loftq_config=None,
    )
    return model, tokenizer


def load_dataset_from_xlsx(file_path):
    """
    Carica un file XLSX e lo converte in un dataset compatibile.
    """
    df = pd.read_excel(file_path)
    dataset = Dataset.from_pandas(df)
    return dataset


def split_dataset(dataset, train_ratio=0.9, original_file_path=None):
    """
    Divide un dataset in training e test set e salva il test set in un file JSON.
    """
    train_size = int(len(dataset) * train_ratio)
    test_size = len(dataset) - train_size
    split_data = dataset.train_test_split(train_size=train_size, test_size=test_size)

    if original_file_path:
        test_folder = os.path.join(os.path.dirname(original_file_path), 'test')
        os.makedirs(test_folder, exist_ok=True)
        test_file_name = os.path.splitext(os.path.basename(original_file_path))[0] + '_test.json'
        test_file_path = os.path.join(test_folder, test_file_name)
        split_data['test'].to_json(test_file_path)
        print(f"Test set salvato in {test_file_path}")

    return split_data


def train_on_dataset(file_path):
    """
    Esegue il fine-tuning su un singolo file XLSX.
    """
    raw_dataset = load_dataset_from_xlsx(file_path)
    model_path = 'base_model'
    model, tokenizer = model_(model_path)
    split_data = split_dataset(raw_dataset, train_ratio=0.8, original_file_path=file_path)
    train_dataset = split_data["train"]

    dpo_trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=TrainingArguments(
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            warmup_ratio=0.1,
            num_train_epochs=30,
            learning_rate=5e-6,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.0,
            lr_scheduler_type="linear",
            seed=42,
            output_dir=f"model/llama_finetuning",
        ),
        beta=0.1,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        max_length=2048,
        max_prompt_length=1024,
    )

    print(f"Starting training for {file_path}...")
    dpo_trainer.train()
    print(f"Training completed for {file_path}. Checkpoints saved in outputs/{os.path.splitext(file_path)[0]}")

    fine_tuned_model_path = f"model"
    model_name = "llama_finetuning"
    load_finetuned_model_into_ollama(fine_tuned_model_path, model_name)


