# 🤖📚 Ask Your PDFs Anything!

Welcome to a tiny robot librarian! 🧑‍🚀📖

This project lets you ask questions about PDF files. The robot reads the books, finds the most helpful pages, and answers using those pages. It also remembers what you said during your visit. 🧠✨

## 🌟 What Is This About?

Imagine a library with two books:

1. A book about **Power Automate** ⚙️
2. A book about **Game of Thrones** 🐉👑

Instead of searching every page yourself, you ask the librarian:

> “How do I make an automatic flow?”

The librarian looks through the right book, finds the closest pages, and gives you a short answer. It also shows where the answer came from. 🎯

This is a document question-answering chatbot. In bigger words, it uses a **retrieve, then answer** idea:

- **Retrieve:** Find useful pieces of the PDFs 🔎
- **Answer:** Ask a local AI to explain those pieces 💬

## 🧩 The Problem: Before and After

### Before 😵

- You have many PDF pages.
- You do not know which page has the answer.
- You scroll, search, and become tired.
- A normal chatbot may guess an answer that is not in your books.

### After 🚀

- Put the PDFs in the `pdfs` folder.
- Ask a question in normal words.
- The project finds related text.
- The AI answers from that text.
- The terminal shows useful source pages and similarity scores.
- The chatbot remembers your conversation.

## 🎬 Our Two Fun Examples

### Example 1: The Power Automate Helper ⚙️

#### Fun story

Sam has a pile of instructions about Power Automate. Sam asks:

> “What does Power Automate help me do?”

Our robot sends the question toward the Power Automate book, like walking to the correct shelf in a library. 📗

#### What the code does

- Opens `power-automate-guidance.pdf`.
- Finds the six text pieces closest to the question.
- Sends those pieces and the chat history to the AI.
- Prints the answer and useful source details.

#### What we learned

🎓 A question can be sent to a smaller, more focused search area. Looking in the right book helps the answer stay on topic.

### Example 2: The Game of Thrones Helper 🐉

#### Fun story

Mia is reading about Westeros and asks:

> “Who is connected to the Iron Throne?”

The robot knows this sounds like the Game of Thrones book, so it checks that shelf instead of mixing the answer with Power Automate instructions. 👑

#### What the code does

- Opens `Game of thrones.pdf`.
- Searches for the six closest text pieces.
- Uses the previous conversation when making the answer.
- Prints source filename, page number, preview text, and score when the match is strong enough.

#### What we learned

🎓 A chatbot can choose a path based on the question. It can also keep separate conversations by using a session name.

### Example 3: The “Maybe Both” Helper 🌍

Sometimes a question is unclear or touches both books. The classifier returns `both`, and the project searches the full collection.

For example:

> “Can you compare the way people and teams work together?”

The robot searches everywhere when it is unsure. When in doubt, it opens the whole library. 🏛️

## 🛠️ How It Works, Step by Step

Think of the program as a friendly library team:

1. **Open the library** 📂  
   The program looks inside the `pdfs` folder.

2. **Read every book** 📖  
   Each PDF page is loaded.

3. **Cut pages into small pieces** ✂️  
   Large pages are split into chunks of about 3,000 characters. Pieces overlap a little so important sentences are not chopped apart.

4. **Give each piece a meaning fingerprint** 🧠  
   An embedding model turns each text piece into numbers that help compare meaning, not just exact words.

5. **Build a fast bookshelf map** 🗺️  
   FAISS stores those fingerprints in `faiss_index/`, so later searches are quick.

6. **Listen to the question** 👂  
   The local `llama3.2:3b` model decides whether the question is about Power Automate, Game of Thrones, or both.

7. **Search the right shelf** 🔎  
   The program gets up to six matching pieces.

8. **Remember the visitor** 🧠  
   A session ID keeps the questions and answers for one chat.

9. **Write a careful answer** ✍️  
   The AI receives the question, chat history, and matching PDF text. It is told to say “I don't know” when the answer is not in the text.

10. **Show the evidence** 🧾  
    Matching sources are printed when their score is below `1.5`. Here, **smaller means more similar**.

11. **Give a goodbye summary** 👋  
    Type `quit` and the program prints a small summary of the session.

## 🚀 How to Run It

### 1. Install the Python packages

Open PowerShell in this project folder:

```powershell
pip install -r requirements.txt
```

### 2. Install and prepare Ollama

This project uses Ollama to run the answering robot on your computer. Install Ollama, then download the model:

```powershell
ollama pull llama3.2:3b
```

Keep Ollama available while the program is running. 🌐

### 3. Check your PDF shelf

Put your PDF files here:

```text
pdfs/
├── Game of thrones.pdf
└── power-automate-guidance.pdf
```

### 4. Start the chatbot

```powershell
python project.py
```

Then:

1. Type your name or another session name.
2. Type a question.
3. Read the answer and source details.
4. Type `quit` to see the session summary.

## 🔁 Reusable Pattern

This same recipe works for many document-chat projects:

```python
# 1. Read documents
documents = load_documents("documents/")

# 2. Break large documents into friendly pieces
chunks = split_into_chunks(documents)

# 3. Turn each piece into a searchable meaning fingerprint
embeddings = make_embeddings(chunks)

# 4. Save the fingerprints in a fast search index
index = build_search_index(embeddings)

# 5. For every question, find the closest pieces
matches = index.search(question, top_k=6)

# 6. Give only the question and useful pieces to the AI
answer = ai_answer(question=question, context=matches)

# 7. Show the answer and where it came from
print(answer)
print(show_sources(matches))
```

### 🎨 Customization Examples

| Use case | Change the pattern to... |
|---|---|
| 🏫 School helper | Put class notes and textbooks in `documents/`. Ask about lessons. |
| 🧑‍⚕️ Clinic handbook | Load approved internal guides and show page numbers with every answer. |
| 🏢 Company helper | Add HR, IT, and finance documents, then route questions to the right shelf. |
| ⚖️ Policy finder | Use a stricter score limit and say “I don't know” for weak matches. |
| 🛠️ Product support | Add manuals and troubleshooting guides so customers can find fixes quickly. |

### ✅ Pattern Checklist

- [ ] Put the right documents in one folder.
- [ ] Read the documents and keep page information.
- [ ] Split very large text into smaller pieces.
- [ ] Build or load a search index.
- [ ] Pick the best few matches for each question.
- [ ] Give the AI the matches as its context.
- [ ] Tell the AI not to invent missing answers.
- [ ] Show source filenames and page numbers.
- [ ] Choose a score limit and test it with real questions.
- [ ] Remember conversations only when the use case needs memory.

### 🏭 Production Tips

- 🔐 Do not put private documents or user questions in logs without permission.
- 📌 Save document version and page metadata with every chunk.
- 🧪 Test easy, hard, unrelated, and “I don't know” questions.
- 📏 Tune the chunk size, number of matches, and score threshold together.
- 🔄 Rebuild the index when PDFs change. Delete `faiss_index/` before rerunning if the old index is stale.
- 🧯 Handle missing folders, broken PDFs, unavailable models, and empty questions kindly.
- 👥 Use a real database for session history when many users need to chat at once.
- 📊 Track answer quality and source quality separately.

### 🌍 Real-World Applications

1. Customer support assistants 💬
2. Employee handbook search 🧑‍💼
3. Research paper helper 🔬
4. School and course-note tutor 🎓
5. Legal or policy document search ⚖️
6. Technical manual assistant 🛠️

### ✨ The Magic Formula

> **Good documents + small searchable pieces + the closest evidence + a careful AI = a helpful document chatbot** 🎯

The AI is not magically reading every book perfectly. We first hand it the most useful pages. That is the important trick. 🪄

## 📁 Files Explained

| File or folder | What it is | Why it matters |
|---|---|---|
| `project.py` | The main robot program | Reads PDFs, searches, chats, remembers, and prints sources |
| `requirements.txt` | Shopping list of Python packages | Tells Python which helpers to install |
| `pdfs/` | The project library | Holds the PDF books to search |
| `pdfs/Game of thrones.pdf` | A sample knowledge book | Demonstrates topic-specific searching |
| `pdfs/power-automate-guidance.pdf` | A sample guidance book | Demonstrates a second topic-specific search |
| `faiss_index/` | The fast bookshelf map | Stores searchable information made from the PDFs |
| `.models/` | Local model cache | Helps keep downloaded embedding files on the computer |
| `venv/` | Python playroom | Keeps installed packages separate from other projects |

## 🧠 Key Concepts

| Concept | Kid-friendly meaning |
|---|---|
| 📄 PDF loader | A helper that opens PDF books |
| ✂️ Text chunking | Cutting big text into bite-sized pieces |
| 🧠 Embeddings | Meaning fingerprints for text |
| 🗺️ FAISS index | A fast map to find similar pieces |
| 🔎 Retrieval | Picking the best pieces for a question |
| 🤖 LLM | A language robot that writes an answer |
| 🧭 Classifier | A traffic helper that chooses the right document path |
| 💬 Chat history | A notebook of earlier questions and answers |
| 🪪 Session ID | A name tag that keeps one visitor's chat separate |
| 📊 Similarity score | A closeness number; in this project, lower is better |
| 🧾 Source metadata | Clues such as filename and page number |

## 🎉 Fun Facts About Why It Matters

- 🗃️ You can turn a messy folder of documents into a question-answering helper.
- 🔍 Searching by meaning can find “automatic workflows” even when the question uses different words.
- 🧠 A small local model can be useful when it receives the right evidence.
- 🧾 Showing sources makes answers easier to check.
- 👨‍👩‍👧 Different session names keep different visitors' conversations apart.
- ⚡ A saved search index means the project does not need to rebuild its bookshelf every time.
- 🚫 The instruction “say I don't know” is a friendly guardrail against made-up answers.

## ⏱️ Summary in 30 Seconds

📚 Put PDFs in `pdfs/`.  
🧩 The program breaks them into pieces.  
🧠 It makes a searchable meaning map.  
🔎 It finds the closest pieces for your question.  
🤖 Ollama writes an answer using those pieces.  
💬 The chatbot remembers your session.  
🧾 The terminal shows useful sources and scores.  

That is it: **ask your books instead of searching every page yourself!** 🚀📖