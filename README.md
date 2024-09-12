# CheatChat APP ⚡🚀

##  🔗 Introduction
------------
The CheatChat App is a `chat-Bot` concerned to answer user Question and this implementation serve our plan.. 

## 🔗 How It Works
------------

![RAG Diagram](src/assets/llm.png)

The application follows these steps to provide responses to your questions:

1. `docement Loading`: The app reads  documents and extracts their text content.

2. `Text Chunking`: The extracted text is divided into smaller chunks that can be processed effectively.

3. `Language Model`: The application utilizes a language model to generate vector representations (embeddings) of the text chunks.

4. `Similarity Matching`: When you ask a question, the app compares it with the text chunks and identifies the most semantically similar ones.

5. `Response Generation`: The selected chunks are passed to the language model, which generates a response based on the relevant content of the docements.

## 🔗 Dependencies and Installation
----------------------------
### To install `the Chatcheat APP`, please follow these steps:

1. ### Clone the repository to your local machine.

2. ### Install the required packages

```bash
$ pip install -r requirements.txt
```

3. ### Setup the environment variables

```bash
$ cp .env.example .env
```
### Set your environment variables in the `.env` file. Like `COHERE_API_KEY` value.

4. ### Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
