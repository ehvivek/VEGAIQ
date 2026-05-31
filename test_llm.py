import sys
import os
os.environ['SSL_CERT_FILE'] = __import__('certifi').where()

from core.granite import chat_response

msg = "Who won Abu Dhabi GP2024 Red Bull Racing ?"
resp = chat_response(msg, [])
print("LLM Response:", resp)
