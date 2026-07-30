import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

NIM_API_KEY = os.environ.get("NIM_API_KEY")
NIM_VL_API_KEY = os.environ.get("NIM_VL_API_KEY", NIM_API_KEY)

vision_client = None
reasoning_client = None

if NIM_API_KEY or NIM_VL_API_KEY:
    try:
        from langchain_nvidia_ai_endpoints import ChatNVIDIA

        if NIM_VL_API_KEY:
            vision_client = ChatNVIDIA(
                model="nvidia/nemotron-nano-12b-v2-vl",
                api_key=NIM_VL_API_KEY,
                temperature=0.2,
                top_p=0.9,
                max_completion_tokens=2048,
            )

        if NIM_API_KEY:
            reasoning_client = ChatNVIDIA(
                model="nvidia/nemotron-3-super-120b-a12b",
                api_key=NIM_API_KEY,
                temperature=0.7,
                top_p=0.95,
                max_tokens=4096,
                reasoning_budget=4096,
                chat_template_kwargs={"enable_thinking": True},
            )
    except Exception:
        vision_client = None
        reasoning_client = None

import json

async def generate_agent_json(prompt: str, fallback_data: dict) -> dict:
    """
    Sends a prompt to the reasoning client, requesting JSON output.
    Returns the parsed JSON dictionary, or the fallback_data if generation fails.
    """
    if not reasoning_client:
        return fallback_data
    
    # Enforce JSON output in the prompt
    full_prompt = prompt + "\n\nCRITICAL INSTRUCTION: You must respond ONLY with a raw JSON object. Do not include markdown formatting (like ```json), commentary, or any other text. Output exactly the JSON."
    
    try:
        # We wrap in a pseudo async way since the Langchain client might be sync or async
        # We'll use the sync invoke method for simplicity, but in a real async environment you'd use ainvoke
        if hasattr(reasoning_client, "ainvoke"):
            response = await reasoning_client.ainvoke([{"role": "user", "content": full_prompt}])
        else:
            response = reasoning_client.invoke([{"role": "user", "content": full_prompt}])
            
        raw_text = response.content
        
        # Cleanup potential markdown wrappers just in case the LLM disobeys
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
        raw_text = raw_text.strip()
        return json.loads(raw_text)
    except Exception as e:
        print(f"LLM parsing error: {e}")
        return fallback_data
