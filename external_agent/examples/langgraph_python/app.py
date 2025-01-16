import logging
import uuid
import time
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from models import ChatCompletionRequest, ChatCompletionResponse, Choice, MessageResponse, DEFAULT_MODEL, Message
from security import get_current_user
from tools import web_search_duckduckgo, news_search_duckduckgo, generate_profile_details, assess_insurance_risk, calculate_insurance_quote
from llm_utils import get_llm_sync, get_llm_stream

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI()

INSURANCE_SYSTEM_PROMPT = """You are a Life insurance assessment agent. When given applicant information, follow these steps in order:
1. Use generate_profile_details to create a detailed profile including health records, lifestyle, occupation, and family health history
2. Use the web search tool to research any relevant health conditions or risk factors that need investigation
3. Use assess_insurance_risk to analyze the complete profile and generate a risk assessment
4. Use calculate_insurance_quote to produce a final quote based on the risk assessment
Execute all steps and provide a final customer-friendly summary of the policy and the quote. Do not ask for additional information - work with what is provided."""

def prepare_insurance_messages(original_messages: List[Message]) -> List[Message]:
    """
    Prepares the message list by injecting the system prompt if it's an insurance-related query
    """
    # Check if the message appears to be insurance-related
    if any(original_messages) and any(keyword in original_messages[-1].content.lower() 
           for keyword in ["insurance", "applicant", "dob", "gender"]):
        
        # Insert system message at the beginning
        return [
            Message(role="system", content=INSURANCE_SYSTEM_PROMPT),
            *original_messages
        ]
    
    return original_messages

@app.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    X_IBM_THREAD_ID: Optional[str] = Header(None, alias="X-IBM-THREAD-ID", description="Optional header to specify the thread ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    logger.info(f"Received POST /chat/completions ChatCompletionRequest: {request.json()}")
    
    # Process thread ID
    thread_id = ''
    if X_IBM_THREAD_ID:
        thread_id = X_IBM_THREAD_ID
    if request.extra_body and request.extra_body.thread_id:
        thread_id = request.extra_body.thread_id
    logger.info("thread_id: " + thread_id)
    
    # Set model
    model = DEFAULT_MODEL
    if request.model:
        model = request.model
    
    # Prepare messages with insurance workflow if needed
    processed_messages = prepare_insurance_messages(request.messages)
    
    # Include all tools including insurance-specific ones
    selected_tools = [
        web_search_duckduckgo, 
        news_search_duckduckgo,
        generate_profile_details,
        assess_insurance_risk,
        calculate_insurance_quote
    ]
    
    if request.stream:
        return StreamingResponse(
            get_llm_stream(processed_messages, model, thread_id, selected_tools), 
            media_type="text/event-stream"
        )
    else:
        last_message, all_messages = get_llm_sync(processed_messages, model, thread_id, selected_tools)
        id = str(uuid.uuid4())
        response = ChatCompletionResponse(
            id=id,
            object="chat.completion",
            created=int(time.time()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=MessageResponse(
                        role="assistant",
                        content=last_message
                    ),
                    finish_reason="stop"
                )
            ]
        )
        return JSONResponse(content=response.dict())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)