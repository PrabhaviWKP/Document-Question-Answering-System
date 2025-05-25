import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import tempfile

load_dotenv()

# Set OpenAI API Key
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment")

os.environ["OPENAI_API_KEY"] = openai_key  # Set once only
# Init FastAPI
app = FastAPI()

#Enable cors for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory FAISS store
vectorstore = None

custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        You are an intelligent assistant used to retrieve context from vector db and answer users question. Use only the context given to answer.

        Context: {context}

        Question: {question}

        Answer:
    """
)


# Endpoint 1: Upload and embed documents
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global vectorstore

    # Save uploaded file temporarily
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    content = await file.read()
    temp_file.write(content)
    temp_file.close()

    # Determine file type
    file_ext = Path(file.filename).suffix.lower()

    # Load based on extension
    if file_ext == ".pdf":
        loader = PyMuPDFLoader(temp_file.name)
    elif file_ext == ".txt":
        loader = TextLoader(temp_file.name, encoding="utf-8")
    else:
        return JSONResponse(status_code=400, content={"error": f"Unsupported file type: {file_ext}"})

    print("running embedding")

    # Load and split
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    # Embed and store in FAISS
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(splits, embeddings)

    return {"message": f"{file.filename} embedded and stored."}

# Endpoint 2: Chat with RAG
@app.post("/chat")
async def chat(query: str = Form(...)):
    if not vectorstore:
        return JSONResponse(status_code=400, content={"error": "No documents uploaded."})

    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(
        model="gpt-4o"
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": custom_prompt}
    )
    response = qa_chain.invoke(query)
    return {"response": response}