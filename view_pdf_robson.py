import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class PDFViewer:
    def __init__(self, root):
        self.root = root
        # Mantém barra de título visível
        self.root.title("Visualizador de PDF")
        self.root.geometry("1000x700+100+100")
        self.root.minsize(600, 400)
        self.root.resizable(True, True)

        # Controle de maximizar/restaurar
        self.is_maximized = False
        self.last_geometry = self.root.geometry()

        # Área PDF com scroll
        self.canvas = tk.Canvas(root, bg="black")
        self.v_scroll = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.v_scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.pack(side="left", fill="y")
        
        # Barra lateral
        self.toolbar = tk.Frame(root, bg="gray20", width=200)
        self.toolbar.pack(side="right", fill="y")
        
        # Botões principais
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
        
        # Pesquisa
        self.entry_search = tk.Entry(self.toolbar)
        self.entry_search.pack(pady=5, padx=10, fill="x")
        
        btn_search = tk.Button(self.toolbar, text="🔎 Buscar", command=self.search_text)
        btn_search.pack(pady=5, padx=10, fill="x")
        
        self.lbl_results = tk.Label(self.toolbar, text="Ocorrências: 0", bg="gray20", fg="white")
        self.lbl_results.pack(pady=5, padx=10, fill="x")
        
        # Botões adicionais
        btn_save = tk.Button(self.toolbar, text="💾 Salvar PDF", command=self.save_pdf)
        btn_save.pack(pady=5, padx=10, fill="x")

        btn_max = tk.Button(self.toolbar, text="⛶ Maximizar/Restaurar", command=self.toggle_maximize)
        btn_max.pack(pady=5, padx=10, fill="x")

        btn_exit = tk.Button(self.toolbar, text="❌ Sair", command=self.root.destroy)
        btn_exit.pack(pady=20, padx=10, fill="x")
        
        # Controle PDF
        self.doc = None
        self.current_page = 0
        self.zoom = 2
        self.file_path = None
        self.last_search = ""

        # Atalhos de teclado
        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<Control-0>", lambda e: self.fit_height())
        self.root.bind("<Control-plus>", lambda e: self.change_zoom(1.2))
        self.root.bind("<Control-minus>", lambda e: self.change_zoom(0.8))
        self.root.bind("<Control-equal>", lambda e: self.change_zoom(1.2))  
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<F3>", lambda e: self.search_text())
        self.root.bind("<Control-m>", lambda e: self.toggle_maximize())

        # Scroll do mouse
        self.canvas.bind_all("<MouseWheel>", self.on_scroll)  
        self.canvas.bind_all("<Button-4>", self.on_scroll)   
        self.canvas.bind_all("<Button-5>", self.on_scroll)   

    # --- Controle janela ---
    def toggle_maximize(self):
        if not self.is_maximized:
            self.last_geometry = self.root.geometry()
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")
            self.is_maximized = True
        else:
            self.root.geometry(self.last_geometry)
            self.is_maximized = False

    # --- PDF ---
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
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)

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

    def fit_height(self):
        if not self.doc: return
        page = self.doc[self.current_page]
        rect = page.rect
        screen_h = self.root.winfo_height()
        self.zoom = screen_h / rect.height
        self.show_page()

    def search_text(self):
        if not self.doc: return
        query = self.entry_search.get() or self.last_search
        if not query: return
        self.last_search = query
        
        page = self.doc[self.current_page]
        results = page.search_for(query)
        
        if not results:
            messagebox.showinfo("Busca", f"'{query}' não encontrado nesta página.")
            self.lbl_results.config(text="Ocorrências: 0")
            return
        
        for rect in results:
            page.add_highlight_annot(rect)
        
        self.lbl_results.config(text=f"Ocorrências: {len(results)}")
        self.show_page()

    def save_pdf(self):
        if self.doc:
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                     filetypes=[("PDF files", "*.pdf")])
            if save_path:
                self.doc.save(save_path)
                messagebox.showinfo("Salvar", f"PDF salvo em:\n{save_path}")

    def on_scroll(self, event):
        if not self.doc: return
        ctrl_pressed = (event.state & 0x0004) != 0
        if ctrl_pressed:
            if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
                self.change_zoom(1.1)
            elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
                self.change_zoom(0.9)
            return
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self.canvas.yview_scroll(-1, "units")
            if self.canvas.yview()[0] <= 0.0:
                self.prev_page()
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self.canvas.yview_scroll(1, "units")
            if self.canvas.yview()[1] >= 1.0:
                self.next_page()

# Iniciar
root = tk.Tk()
app = PDFViewer(root)
root.mainloop()