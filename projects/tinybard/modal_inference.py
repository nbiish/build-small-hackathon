import os
import modal

# Define the Modal app
app = modal.App("tinybard-inference")

# Use a standard CUDA image with vLLM installed
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "vllm==0.5.4",
        "huggingface_hub",
        "fastapi",
        "uvicorn",
    )
)

# Default model (can be overridden via environment variable)
MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")


@app.cls(
    gpu="L4",  # L4 is cost-efficient and widely available
    image=image,
    secrets=[modal.Secret.from_name("huggingface-secret")],  # Optional, for gated models
    timeout=600,
)
class InferenceModel:
    @modal.enter()
    def load_model(self):
        from vllm import AsyncLLMEngine
        from vllm.engine.arg_utils import AsyncEngineArgs

        # Configure AsyncLLMEngine
        engine_args = AsyncEngineArgs(
            model=MODEL_ID,
            max_model_len=2048,
            gpu_memory_utilization=0.9,
            trust_remote_code=True,
        )
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        log_info = f"Model {MODEL_ID} loaded successfully."
        print(log_info)

    @modal.method()
    async def generate(self, prompt: str, max_tokens: int = 226, temperature: float = 0.7) -> str:
        from vllm import SamplingParams
        import uuid

        sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
        )
        request_id = str(uuid.uuid4())
        results_generator = self.engine.generate(prompt, sampling_params, request_id)

        final_output = None
        async for request_output in results_generator:
            final_output = request_output

        if final_output and final_output.outputs:
            return final_output.outputs[0].text
        return ""


# Create a FastAPI wrapper to expose an OpenAI-compatible /v1/chat/completions endpoint
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

web_app = FastAPI(title="TinyBard Inference API")


@web_app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", MODEL_ID)
    max_tokens = body.get("max_tokens", 220)
    temperature = body.get("temperature", 0.7)

    # Translate chat messages to plain text prompt (standard ChatML or basic dialogue)
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "").strip()
        if role == "system":
            prompt += f"System Instructions:\n{content}\n\n"
        elif role == "user":
            prompt += f"User:\n{content}\n\n"
        elif role == "assistant":
            prompt += f"Assistant:\n{content}\n\n"
    prompt += "Assistant:\n"

    # Call the Modal class method
    try:
        model_instance = InferenceModel()
        text = await model_instance.generate.remote.aio(
            prompt, max_tokens=max_tokens, temperature=temperature
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Modal inference failed: {str(e)}")

    # Return OpenAI-compatible JSON structure
    return JSONResponse(
        {
            "id": "chatcmpl-modal",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text.strip(),
                    },
                    "finish_reason": "stop",
                }
            ],
        }
    )


# Expose the web app via Modal ASGI
@app.function(image=image)
@modal.asgi_app()
def api():
    return web_app
