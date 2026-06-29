import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from app.core.config import settings

class LlmService:
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._pipe = None

    def _ensure_loaded(self):
        if self._pipe is None:
            model_id = settings.llm_model
            print(f"Loading local LLM model: {model_id}...")
            self._tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Auto-detect CUDA
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")
            
            self._model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(device)
            
            self._pipe = pipeline(
                "text-generation",
                model=self._model,
                tokenizer=self._tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                device=0 if device == "cuda" else -1
            )
            print("Local LLM model loaded successfully.")

    def generate(self, prompt: str) -> str:
        self._ensure_loaded()
        messages = [
            {"role": "user", "content": prompt}
        ]
        try:
            formatted_prompt = self._tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            outputs = self._pipe(formatted_prompt, return_full_text=False)
            return outputs[0]['generated_text']
        except Exception as e:
            # Fallback if chat template is not supported by tokenizer
            outputs = self._pipe(prompt, return_full_text=False)
            return outputs[0]['generated_text']

llm_service = LlmService()
