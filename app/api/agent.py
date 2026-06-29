from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.agents.copilot_agent import copilot_agent

router = APIRouter()

class RagRequest(BaseModel):
    question: str

class RagResponse(BaseModel):
    answer: str

@router.post("/ask", response_model=RagResponse)
async def ask(request: RagRequest):
    try:
        initial_state = {
            "question": request.question,
            "history": [],
            "thought_log": [],
            "next_tool": None,
            "next_tool_args": None,
            "final_answer": None
        }
        
        # Invoke LangGraph agent loop
        result = copilot_agent.invoke(initial_state)
        answer = result.get("final_answer")
        
        if not answer:
            answer = "I could not formulate an answer to your query."
            
        return RagResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
