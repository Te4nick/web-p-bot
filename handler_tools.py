import os
import dialogflow_v2 as dialogflow
import telegram
import logging 
import time

# Путь к json файлу dialogflow
os.environ[""]=""

# ID проекта в dialogflow
project_id = ""

# Токен основного бота телеграм
telegram_token = ""
#telegram_token = ""

# Токен бота логов телеграм
telegram_token_information_message = ""

# Пользователь телеграм для логов
chat_id_information_message = ''

# Токен группы ВК
vk_community_token = ""

# Возвращается ответ из dialogflow
def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.types.TextInput(
                text=text, language_code=language_code)

    query_input = dialogflow.types.QueryInput(text=text_input)
    
    response = session_client.detect_intent(
            session=session, query_input=query_input)
    
    if response.query_result.intent.is_fallback:
        return None
    else:
        return response.query_result.fulfillment_text

# Отправляются логи в случае ошибки 
class MyLogsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        bot_error = telegram.Bot(token=telegram_token_information_message)
        bot_error.send_message(chat_id=chat_id_information_message, text=log_entry)
