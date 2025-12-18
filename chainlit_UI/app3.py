import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

SYSTEM_MESSAGE = """
Analyze this resume for a Data Scientist role. Return JSON format with Name, Status, and Reason.
"""

FINAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MESSAGE),
    ("user", "resume: {resume_content}")
])

class RESUME_SHORTLISTER:
    def __init__(self, path, model_choice):
        self.path = path
        self.model_choice = model_choice.lower()
        self.groq_llm = ChatGroq(api_key=os.getenv('GROQ_API_KEY'), model_name='llama-3.3-70b-versatile')
        self.openai_llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")

    def text_extractor(self):
        loader = PyPDFLoader(self.path)
        return " ".join([p.page_content for p in loader.load()])

    def get_chain(self, use_fallback=False):
        if use_fallback:
            llm = self.groq_llm if self.model_choice == 'openai' else self.openai_llm
        else:
            llm = self.openai_llm if self.model_choice == 'openai' else self.groq_llm
        return FINAL_PROMPT | llm | StrOutputParser()
