# import requests

# api_key = "2dd136a436c563b3916d4c5031190665"

# url = "https://gnews.io/api/v4/search"

# params = {
#     "apikey": api_key,
#     "q": "NVIDIA",
#     "lang": "es",
#     "max": 5
# }

# response = requests.get(url, params=params)

# print("STATUS:", response.status_code)
# print("RESPUESTA:", response.text)

from memory.memory_service import MemoryService
from core.interpretation_result import InterpretationResult
from core.request import AgentRequest

memory = MemoryService()

session_id = memory.create_session()

request_id = memory.save_request(
    session_id,
    "¿Qué tiempo hace en Madrid?"
)

request = AgentRequest(
    intent="weather",
    action="get_weather",
    parameters={"city": "Madrid"},
    context={},
    requests=[]
)

interpretation = InterpretationResult(
    request=request,
    raw_json={
        "intent": "weather",
        "action": "get_weather",
        "parameters": {
            "city": "Madrid"
        },
        "context": {},
        "requests": []
    },
    model="qwen3:14b",
    total_duration=1500000000,
    load_duration=500000000,
    prompt_eval_duration=400000000,
    eval_duration=600000000,
    eval_count=25
)

interpretation_id = memory.save_interpretation(
    request_id,
    interpretation
)

print("session_id:", session_id)
print("request_id:", request_id)
print("interpretation_id:", interpretation_id)