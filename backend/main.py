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

# load variables from .env file
load_dotenv()

# Set to use OpenAI API key from .env file
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment")

# Set the API key as an environment variable
os.environ["OPENAI_API_KEY"] = openai_key

# Fast API initialization
app = FastAPI()

#Cors for connect the system with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# in-memory FAISS vectore which used to store embeddings
vectorstore = None

# Custom prompt to guide the model to get the response from the retrieved context
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        You are an intelligent assistant used to retrieve context from vector db and answer users question. Use only the context given to answer.

        Context: {context}

        Question: {question}

        Answer:
    """
)


# Document uploading and embedding endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global vectorstore

    # Saving uploaded file in a temporary location
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    content = await file.read()
    temp_file.write(content)
    temp_file.close()

    # Detect the type of the file (pdf/txt)
    file_ext = Path(file.filename).suffix.lower()

    # Load based on the extension of the uploaded file
    if file_ext == ".pdf":
        loader = PyMuPDFLoader(temp_file.name)
    elif file_ext == ".txt":
        loader = TextLoader(temp_file.name, encoding="utf-8")
    else:
        return JSONResponse(status_code=400, content={"error": f"Unsupported file type: {file_ext}"})

    print("running embedding")

    # Load the document and split it into managable chunks
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)

    # Embed the chunks using OpenAI embeddings and store in FAISS for future use
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(splits, embeddings)

    return {"message": f"{file.filename} embedded and stored."}

# Chat(ask questions) about the uploaded document using this endpoint.
@app.post("/chat")
async def chat(query: str = Form(...)):
    # Before proceeding make sure the document is correctly uploaded and embedded
    if not vectorstore:
        return JSONResponse(status_code=400, content={"error": "No documents uploaded."})

    # Define retriever from vectorstore
    retriever = vectorstore.as_retriever()

    # the LLM model
    llm = ChatOpenAI(
        model="gpt-4o"
    )

    # Build the Q&A chain using the above defined retriever and the custom prompt
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": custom_prompt}
    )

    # Run the Q&A chain
    response = qa_chain.invoke(query)
    return {"response": response}