# Document Based Question Answering System
This system allows users to upload .pdf or .txt files and ask questions about the document to get accurate answers from the uploaded document. This uses ***Langchain***, _**OpenAI**, **FAISS**,_ _**FASTAPLI**_ for backend and _**react-vite**_ for frontend.
After some researches on the same domain I came up with openAI(gpt 4o) because the model generally perform well comparing to the other platforms like Mistral and QwenAI. OpenAI has a larger model size, extensive training data and fine tuned for specific tasks. While the Mistal and QwenAI offer advantages in cost the OpenAI's performance was significant.

# Features
- Upload .pdf or .txt documents
- Extract, embed, store text using FAISS
- Ask questions from the uploaded document
- Get answers for the questions from GPT-4o powered by OpenAI
- Simple and interactive frontend for users

# Technologies Used
## Backend 
- FASTAPI - API Framework
- LangChain - Simplifies the LLM application
- FAISS - Vector Storage that allows search for embeddings of multimedia documents that are similar to each other.
- OpenAI - gpt-4o for answering questions
- dotenv - For managing API keys

## Frontend
- React (Vite + TypeScript)
- Tailwind CSS
- shadcn/ui - Styled UI components

# Setup Instructions 
1. Clone the repository
   - git clone https://github.com/your username/doc_qa_API
   - cd doc_qa_API
2. Backend Setup
   1. Install dependencies
       - cd backend
       - pip install -r requirements.txt
   2. Add .env file
       - inside the backend directory create .env file 
       - OPENAI_API_KEY = your-openai-api-key
   3. Run the backend server
       - uvicorn main:app --reload
3. Frontend Setup
   1. cd frontend
   2. npm install
   3. npm run dev
      - This will launch the frontend. In that select the localhost link (appearing in the terminal). Then you will redirect to the frontend of the system
4. Make sure to run both the backend and frontend before working on the system. 
   
# Demo Video of the system 


https://github.com/user-attachments/assets/35aa1f3a-a110-4077-bf73-2d66c40da4be


# References Used 
- https://python.langchain.com/docs/tutorials/llm_chain/
- https://ui.shadcn.com/docs/installation/vite
- https://www.langchain.com/





