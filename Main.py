import os
import sys
import io
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import nltk
import PyPDF2
import docx
import faiss
import numpy as np
import openai
from dotenv import load_dotenv

class DocumentSimilarityApp:
    def __init__(self, master):
        self.master = master
        master.title("Document Similarity Search")
        master.geometry("600x550")

        # Load API key
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            messagebox.showerror("Error", "OPENAI_API_KEY not found in .env file")
            sys.exit(1)

        # Global variables for FAISS index
        self.global_index = None
        self.all_chunks = []

        # Ensure NLTK downloads
        self._silent_nltk_download()

        # Create GUI elements
        self._create_widgets()

    def _silent_nltk_download(self):
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            print(f"NLTK download error: {e}")

    def _create_widgets(self):
        # Strategy selection
        tk.Label(self.master, text="Choose Chunking Strategy:").pack(pady=5)
        self.strategy_var = tk.StringVar(value="sentence")
        strategies = [("Sentence", "sentence"), 
                      ("Paragraph", "paragraph"), 
                      ("Overlap", "overlap")]
        for text, value in strategies:
            tk.Radiobutton(self.master, text=text, variable=self.strategy_var, 
                           value=value).pack()

        # File upload button
        self.upload_button = tk.Button(self.master, text="Upload File", command=self._upload_file)
        self.upload_button.pack(pady=5)

        # Loading spinner
        self.loading_frame = tk.Frame(self.master)
        self.loading_frame.pack(pady=5)
        self.loading_label = tk.Label(self.loading_frame, text="Processing...")
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', length=200)
        
        # Query input
        tk.Label(self.master, text="Enter Search Query:").pack()
        self.query_entry = tk.Entry(self.master, width=50)
        self.query_entry.pack(pady=5)

        # Search button
        tk.Button(self.master, text="Search", command=self._search_similarity).pack(pady=5)

        # Results display
        tk.Label(self.master, text="Results:").pack()
        self.results_text = scrolledtext.ScrolledText(self.master, height=10, width=70, wrap=tk.WORD)
        self.results_text.pack(pady=10)

    def _show_loading(self):
        self.upload_button.config(state=tk.DISABLED)
        self.loading_label.pack()
        self.progress.pack()
        self.progress.start()

    def _hide_loading(self):
        self.upload_button.config(state=tk.NORMAL)
        self.loading_label.pack_forget()
        self.progress.pack_forget()
        self.progress.stop()

    def _upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")]
        )
        if file_path:
            # Start processing in a separate thread
            threading.Thread(target=self._threaded_process_document, 
                             args=(file_path, self.strategy_var.get()), 
                             daemon=True).start()

    def _threaded_process_document(self, file_path, strategy):
        # Show loading spinner
        self.master.after(0, self._show_loading)

        try:
            # Process document
            self._process_document(file_path, strategy)
            
            # Show success message
            self.master.after(0, lambda: messagebox.showinfo("Success", "Document processed successfully"))
        
        except Exception as e:
            # Show error message
            self.master.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        finally:
            # Hide loading spinner
            self.master.after(0, self._hide_loading)

    def _process_document(self, file_path, strategy):
        # Text extraction
        if file_path.endswith('.pdf'):
            text = self._extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = self._extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

        # Chunk text based on strategy
        if strategy == 'sentence':
            chunks = self._sentence_splitter(text)
        elif strategy == 'paragraph':
            chunks = self._paragraph_splitter(text)
        elif strategy == 'overlap':
            chunks = self._overlap_size_splitter(text)
        else:
            raise ValueError("Invalid strategy")

        # Generate embeddings
        embeddings = self._generate_openai_embeddings(chunks)
        if not embeddings:
            raise ValueError("Failed to generate embeddings")

        # Update global index
        self._add_to_global_index(embeddings, chunks)

    def _search_similarity(self):
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return

        if self.global_index is None:
            messagebox.showwarning("Warning", "Please upload a document first")
            return

        try:
            # Generate query embedding
            query_embedding = self._generate_openai_embeddings([query])
            query_embedding_array = np.array(query_embedding, dtype='float32')

            # Search global index
            distances, indices = self.global_index.search(query_embedding_array, k=1)
            
            # Display results
            most_similar_chunk = self.all_chunks[indices[0][0]]
            result_text = f"Most Similar Chunk (Distance: {distances[0][0]}):\n{most_similar_chunk}"
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, result_text)

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

    def _extract_text_from_pdf(self, file_path):
        try:
            reader = PyPDF2.PdfReader(file_path)
            text = ''.join(page.extract_text() for page in reader.pages)
            return text
        except Exception as e:
            raise ValueError(f"PDF reading error: {e}")

    def _extract_text_from_docx(self, file_path):
        try:
            doc = docx.Document(file_path)
            return '\n\n'.join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"DOCX reading error: {e}")

    def _sentence_splitter(self, text):
        try:
            return nltk.sent_tokenize(text)
        except Exception as e:
            messagebox.showwarning("Warning", f"Sentence splitting error: {e}")
            return text.split('. ')

    def _paragraph_splitter(self, text):
        return [p.strip() for p in text.splitlines() if p.strip()]

    def _overlap_size_splitter(self, text, chunk_size=200, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(' '.join(words[i:i + chunk_size]))
        return chunks

    def _generate_openai_embeddings(self, chunks):
        embeddings = []
        try:
            for chunk in chunks:
                response = openai.embeddings.create(
                    input=chunk,
                    model="text-embedding-ada-002"
                )
                embeddings.append(response.data[0].embedding)
            return embeddings
        except Exception as e:
            messagebox.showerror("Error", f"Embedding generation error: {e}")
            return []

    def _add_to_global_index(self, new_embeddings, new_chunks):
        try:
            embeddings_array = np.array(new_embeddings, dtype='float32')
            
            if self.global_index is None:
                dimension = embeddings_array.shape[1]
                self.global_index = faiss.IndexFlatL2(dimension)
            
            self.global_index.add(embeddings_array)
            self.all_chunks.extend(new_chunks)
        except Exception as e:
            messagebox.showerror("Error", f"Index update error: {e}")

def main():
    root = tk.Tk()
    app = DocumentSimilarityApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()