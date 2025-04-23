# sk-0da58544c63c489d95c41e39bf459cff
from openai import OpenAI


class CDeepSeek:
    def __init__(self):
        self.client = OpenAI(api_key="sk-0da58544c63c489d95c41e39bf459cff", base_url="https://api.deepseek.com")


