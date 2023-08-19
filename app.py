from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import os 
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

app = Flask(__name__)

load_dotenv()

os.getenv("OPENAI_API_KEY")

app_directory = os.path.abspath(os.path.dirname(__file__))

# Define the relative path to the PDF file
pdf_filename = "tariff2.pdf"

# Construct the absolute path to the PDF file
pdf_path = os.path.join(app_directory, pdf_filename)

knowledge_base = None
chain = None
messages = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global knowledge_base, chain
    
    if request.method == "POST":
        api_key = request.form["api-key"]
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            
            pdf = "tariff2.pdf"
            
            if pdf is not None:
                pdf_reader = PdfReader(pdf)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                    
                
                
                text_splitter = CharacterTextSplitter(
                    separator="\n",
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len
                )
                
                chunks = text_splitter.split_text(text=text)
        
                embeddings = OpenAIEmbeddings()
                knowledge_base = FAISS.from_texts(chunks, embeddings)
                
                chain = load_qa_chain(OpenAI(), chain_type="stuff")
        
    return render_template("index.html", messages=messages)

@app.route('/ask', methods=['POST'])
def ask_question():
    global messages

    if request.method == 'POST':
        user_question = request.form.get('user-question')

        if knowledge_base is not None and chain is not None:
            # Perform question-answering here
            docs = knowledge_base.similarity_search(user_question)
            result = chain.run(input_documents=docs, question=user_question)
            

            # Check if result is a dictionary with 'answers' key
            

            # Add user's question and response to messages
            messages.append(f'You: {user_question}')
            messages.append(f'AI: {result}')

    return render_template("index.html", messages=messages)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)