from llama_cpp import Llama

class LlamaEngine:
    def __init__(self):
        self.model_path = "/workspaces/sulee_ki/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_threads=4
        )

    def generate(self, prompt: str) -> str:
        response = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.9
        )
        return response["choices"][0]["text"].strip()
