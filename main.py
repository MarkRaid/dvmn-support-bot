import logging

from google.cloud import dialogflow_v2 as dialogflow

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from dotenv import dotenv_values

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

config = dotenv_values(".env")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Здравствуйте")


async def get_dialog_response(session_id, text, language_code='ru'):
    session_client = dialogflow.SessionsAsyncClient()

    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    request = dialogflow.DetectIntentRequest(
        session=session,
        query_input=query_input,
    )

    response = await session_client.detect_intent(request)

    return response


async def dialog_with_dialogflow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session_id = update.effective_chat.id
    response = await get_dialog_response(session_id, update.message.text)
    if not response.query_result.fulfillment_text:
        await update.message.reply_text("Переключаю наш диалог на сотрудника")
        return
    await update.message.reply_text(response.query_result.fulfillment_text)


def main() -> None:
    global project_id
    project_id = config["GOOGLE_PROJECT_ID"]

    token = config["TELEGRAM_BOT_TOKEN"]

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, dialog_with_dialogflow))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
