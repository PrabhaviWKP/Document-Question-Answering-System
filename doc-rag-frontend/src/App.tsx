import { useState } from 'react'
import './App.css'
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Main Component
export default function App() {

  // Selected file
  const [file, setFile] = useState<File | null>(null);

  // Question input from the user
  const [query, setQuery] = useState("");

  //Answer to the question
  const [response, setResponse] = useState("");

  // loading status (document uploading/uploaded, question asking
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [asking, setAsking] = useState(false);

  // Prompt a message when the document uploaded
  const [docUploadStatus, setDocUploadStatus] = useState("");

  // Document upload handling
  const uploadDocument = async () => {
  if (!file) return alert("Please select a file!");

  const formData = new FormData();
  formData.append("file", file);

  setUploading(true); // show uploading status of the document
  try {
    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    setUploaded(true); // Mark as document uploaded
    setDocUploadStatus(data.message) // Display success message
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    alert("Upload failed");
    setUploaded(false)
  } finally {
    setUploading(false);
  }
};

  //Send question to the backend and get answer
const askQuestion = async () => {
  if (!uploaded) return alert("Please upload a document first.");
  if (!query.trim()) return alert("Please enter a question");

  const formData = new FormData();
  formData.append("query", query);

  setAsking(true);
  try {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setResponse(data.response.result);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    alert("Failed to get response");
  } finally {
    setAsking(false);
  }
};


  return (
    <div className="container mx-auto p-6 space-y-8">
      <h1 className="text-3xl font-bold">Document Question & Answering Chat</h1>

      <div className="mx-auto lg:flex space-y-5 gap-8 items-start pt-10">

            <div className="space-y-3 w-full lg:w-[1/2]">
              <div className="w-full flex gap-2">
              <Input
                type="file"
                accept=".pdf,.txt"
                placeholder={"Select a file"}
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <Button type="button" onClick={uploadDocument} disabled={uploading}>
                {uploading ? "Uploading..." : "Upload Document"}
              </Button>
                </div>

              {docUploadStatus &&
                <div className="border rounded p-4 text-left">
                  {docUploadStatus}
                </div>
              }
            </div>

            <div className="w-full space-y-5">
              <h2 className="font-medium text-md text-start">Type your question below, to query from the uploaded document</h2>
              <div className="flex flex-col items-end space-y-3">
              <Textarea
                placeholder="Ask a question about the document"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={4}
                disabled={!uploaded}
              />
              <Button type="button" onClick={askQuestion} disabled={!uploaded || asking}>
                {asking ? "Thinking..." : "Ask"}
              </Button>
                {response && (
              <div className="p-4 border rounded bg-gray-50 text-left">
                <h2 className="font-semibold mb-2">Answer:</h2>
                <p>{response}</p>
              </div>
            )}
              </div>
            </div>

          </div>
    </div>
  );
}
