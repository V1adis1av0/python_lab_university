import tkinter as tk
from tkinter import messagebox


# ===== ЛОГИКА (бывший lab1) =====

alpha = ['a', 'b', 'c', 'd', 'e','f', 
         'g', 'h', 'i', 'j','k', 'l', 
         'm', 'n', 'o', 'p', 'q', 'r', 
         's', 't', 'u', 'v', 'w', 'x', 
         'y', 'z', '.', ',', '!', '?', 
         ';', ':', '%', ' ', '(', ')']


def encrypt(text: str) -> str:
    result = []
    offset = 30

    for char in text.lower():
        if char not in alpha:
            raise ValueError(f"Недопустимый символ: {char}")
        result.append(alpha[alpha.index(char) - offset])

    return "".join(result)


def decrypt(text: str) -> str:
    result = []
    offset = 6

    for char in text:
        if char not in alpha:
            raise ValueError(f"Недопустимый символ: {char}")
        result.append(alpha[alpha.index(char) - offset])

    return "".join(result)


# ===== GUI =====

class PolybiusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Polybius Cipher")
        self.center_window(500, 300)

        # Растягивание
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # ===== Ввод =====
        self.input_label = tk.Label(root, text="Введите текст:")
        self.input_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.input_text = tk.Entry(root)
        self.input_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Enter = encrypt
        self.input_text.bind("<Return>", lambda event: self.encrypt_text())

        # ===== Кнопки =====
        button_frame = tk.Frame(root)
        button_frame.grid(row=2, column=0, pady=10)

        tk.Button(button_frame, text="Encrypt", width=12,
                  command=self.encrypt_text).pack(side="left", padx=5)

        tk.Button(button_frame, text="Decrypt", width=12,
                  command=self.decrypt_text).pack(side="left", padx=5)

        tk.Button(button_frame, text="Очистить", width=12,
                  command=self.clear).pack(side="left", padx=5)

        # ===== Вывод =====
        self.output_label = tk.Label(root, text="Результат:", anchor="w")
        self.output_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.output_text = tk.Text(root, height=4)
        self.output_text.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

    # ===== ЛОГИКА КНОПОК =====

    def encrypt_text(self):
        try:
            text = self.input_text.get()
            result = encrypt(text)

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def decrypt_text(self):
        try:
            text = self.input_text.get()
            result = decrypt(text)

            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, result)

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def clear(self):
        self.input_text.delete(0, tk.END)
        self.output_text.delete("1.0", tk.END)

    # ===== УТИЛИТЫ =====

    def center_window(self, width, height):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)

        self.root.geometry(f"{width}x{height}+{x}+{y}")


# ===== ЗАПУСК =====

if __name__ == "__main__":
    root = tk.Tk()
    app = PolybiusApp(root)
    root.mainloop()