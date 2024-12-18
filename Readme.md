# Document Similarity Search Application

This is a **Document Similarity Search Application** built using Python. The program processes text files (PDF and DOCX), splits their content into chunks using different strategies, generates embeddings using the **OpenAI API**, and searches for the most similar text chunk to a user query using a **FAISS vector database**.

The application features a **graphical user interface (GUI)** using Tkinter, allowing users to:
1. Select a chunking strategy (sentence, paragraph, or overlap-based splitting).
2. Upload PDF or DOCX files.
3. Search for text similarities by entering a query.
4. View the most similar chunk of text with its similarity distance.

---

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Running the Program](#running-the-program)
5. [How to Use the Application](#how-to-use-the-application)
6. [Chunking Strategies](#chunking-strategies)
7. [Troubleshooting](#troubleshooting)
8. [Acknowledgements](#acknowledgements)

---

## Features
- **Graphical User Interface**: An easy-to-use interface to interact with the program.
- **Text Chunking**: Supports three chunking strategies:
  - Sentence-based splitting
  - Paragraph-based splitting
  - Overlapping fixed-size splitting
- **OpenAI Embeddings**: Generates embeddings for text chunks using the **OpenAI Embedding API**.
- **FAISS Vector Search**: Stores embeddings in a FAISS index for fast similarity search.
- **File Support**: Accepts both PDF and DOCX file formats.
- **Search Query**: Allows users to input a query to retrieve the most similar text chunk.
- **Loading Spinner**: Displays progress during file processing.

---

## Requirements
To run this project, ensure you have the following installed:

1. Python **3.8+**
2. OpenAI API Key (stored in a `.env` file)
3. Required Python libraries:
    - `openai`
    - `nltk`
    - `numpy`
    - `faiss-cpu`
    - `python-docx`
    - `PyPDF2`
    - `python-dotenv`
    - `tkinter` (usually included with Python)

---

## Installation

### 1. Clone the Repository
```bash
git clone <repository-link>
cd <repository-folder>
```

### 2. Set Up the Environment
1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

2. **Install Required Packages**:
```bash
pip install -r requirements.txt
```

> **Note**: Ensure your OpenAI API key is set up in a `.env` file in the project directory.

### 3. Create the `.env` File
Create a file named `.env` in the project directory and add your OpenAI API key:
```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```
Replace `your_openai_api_key_here` with your actual API key.

---

## Running the Program

To run the application, execute the following command in the terminal:
```bash
python main.py
```

---

## How to Use the Application

1. **Launch the Program**:
   - Run the script using the terminal command.
   - A GUI window will appear.

2. **Select a Chunking Strategy**:
   - Choose one of the three chunking strategies: `Sentence`, `Paragraph`, or `Overlap`.

3. **Upload a File**:
   - Click on the "Upload File" button and select a PDF or DOCX file.
   - The program will process the file, split the text into chunks, and generate embeddings.
   - A success message will appear when the process completes.

4. **Enter a Search Query**:
   - Type a query into the input box labeled "Enter Search Query".
   - Click the "Search" button to find the most similar text chunk.

5. **View Results**:
   - The most similar text chunk, along with its similarity distance, will be displayed in the results area.

---

## Chunking Strategies

1. **Sentence Splitting**:
   - Splits text into sentences using NLTK's `sent_tokenize` method.
   - Best for documents with well-defined sentences.

2. **Paragraph Splitting**:
   - Splits text based on single newlines.
   - Ideal for documents with clear paragraph breaks.

3. **Overlap-Based Splitting**:
   - Splits text into fixed-size chunks with overlapping words to preserve context.
   - Useful for long, continuous text without clear boundaries.


Enjoy the project!
