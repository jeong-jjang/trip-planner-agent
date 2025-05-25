import os
from dotenv import load_dotenv
load_dotenv()  
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
llm_4 = ChatOpenAI(model="gpt-4o")