from fastapi import APIRouter
import os
from fastapi import  Query,HTTPException
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse

load_dotenv()

router = APIRouter(
    prefix="/webhooks/whatsapp",
    tags = ["whatsapp"])


WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
@router.get("")
async def get_whataspp_status(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):

    if hub_mode == "subscribe" and hub_verify_token==WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)

    else:
        raise HTTPException(
            status_code = 403
        )


@router.post("",status_code=200)
def post_message(payload: dict):
    sender_id =  payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]

    message_text = payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

    return {"sender_id":sender_id,"message_text":message_text}
     