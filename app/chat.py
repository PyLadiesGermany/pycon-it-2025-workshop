import requests
import time
from dotenv import load_dotenv

from ecologits._ecologits import EcoLogits
from ecologits.tracers.utils import llm_impacts

load_dotenv()

MOCK_CHAT_URL = "http://mock_chat:8002/chat"
MOCK_PROVIDER = "openai"
MODEL_TO_MOCK = "gpt-4o-mini"


def get_chat_emissions(text: str) -> dict:
    """
    Calls the mock chat service and then computes emission metrics via Ecologits.
    Returns a dict with keys:
      - 'chat_response': the JSON body from the mock chat
      - 'emissions': the result from calculate_emissions()
    """
    timer_start = time.perf_counter()
    # Call the mock chat service
    payload = {"model": MODEL_TO_MOCK, "messages": [{"role": "user", "content": text}]}
    resp = requests.post(MOCK_CHAT_URL, json=payload)
    resp.raise_for_status()
    response = resp.json()
    request_latency = time.perf_counter() - timer_start

    # TODO: log these emission metrics to Prometheus
    impacts = llm_impacts(
        provider=MOCK_PROVIDER,
        model_name=MODEL_TO_MOCK,
        output_token_count=response["usage"]["completion_tokens"],
        request_latency=request_latency,
        electricity_mix_zone=EcoLogits.config.electricity_mix_zone,
    )

    return {
        "chat_response": response["choices"][0]["message"]["content"],
        "emissions": {
            "energy": f"{impacts.energy.value} {impacts.energy.unit}",
            "pe": f"{impacts.pe.value} {impacts.pe.unit}",
            "adpe": f"{impacts.adpe.value} {impacts.adpe.unit}",
            "gwp": f"{impacts.gwp.value} {impacts.gwp.unit}",
        },
    }
