import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class PDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de PDF")
        
        # Área de exibição central
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Barra lateral
        self.toolbar = tk.Frame(root, bg="gray20", width=150)
        self.toolbar.pack(side="right", fill="y")
        
        # Botões da barra lateral
        btn_open = tk.Button(self.toolbar, text="📂 Abrir PDF", command=self.open_pdf)
        btn_open.pack(pady=5, padx=10, fill="x")
        
        btn_prev = tk.Button(self.toolbar, text="⬅ Página Anterior", command=self.prev_page)
        btn_prev.pack(pady=5, padx=10, fill="x")
        
        btn_next = tk.Button(self.toolbar, text="➡ Próxima Página", command=self.next_page)
        btn_next.pack(pady=5, padx=10, fill="x")
        
        btn_zoom_in = tk.Button(self.toolbar, text="🔍 Zoom +", command=lambda: self.change_zoom(1.2))
        btn_zoom_in.pack(pady=5, padx=10, fill="x")
        
        btn_zoom_out = tk.Button(self.toolbar, text="🔎 Zoom -", command=lambda: self.change_zoom(0.8))
        btn_zoom_out.pack(pady=5, padx=10, fill="x")
        
        self.entry_search = tk.Entry(self.toolbar)
        self.entry_search.pack(pady=5, padx=10, fill="x")
        
        btn_search = tk.Button(self.toolbar, text="🔎 Buscar", command=self.search_text)
        btn_search.pack(pady=5, padx=10, fill="x")
        
        btn_save = tk.Button(self.toolbar, text="💾 Salvar PDF", command=self.save_pdf)
        btn_save.pack(pady=5, padx=10, fill="x")
        
        # Variáveis de controle
        self.doc = None
        self.current_page = 0
        self.zoom = 2  # fator inicial de zoom
    
    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.doc = fitz.open(file_path)
            self.file_path = file_path
            self.current_page = 0
            self.show_page()
    
    def show_page(self):
        if not self.doc: return
        page = self.doc[self.current_page]
        
        # Renderizar página com zoom
        matrix = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=matrix)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.tk_img = ImageTk.PhotoImage(img)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.show_page()
    
    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.show_page()
    
    def change_zoom(self, factor):
        if self.doc:
            self.zoom *= factor
            self.show_page()
    
    def search_text(self):
        if not self.doc: return
        query = self.entry_search.get()
        if not query: return
        
        page = self.doc[self.current_page]
        results = page.search_for(query)
        
        if not results:
            messagebox.showinfo("Busca", f"'{query}' não encontrado nesta página.")
            return
        
        # Marcar os resultados
        for rect in results:
            page.add_highlight_annot(rect)
        
        self.show_page()
    
    def save_pdf(self):
        if self.doc:
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     filetypes=[("PDF files", "*.pdf")])
            if save_path:
                self.doc.save(save_path)
                messagebox.showinfo("Salvar", f"PDF salvo em:\n{save_path}")

# Iniciar aplicação
root = tk.Tk()
app = PDFViewer(root)
root.mainloop()
