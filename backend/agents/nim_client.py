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
