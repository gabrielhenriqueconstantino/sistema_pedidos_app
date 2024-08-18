import tkinter as tk
from tkinter import messagebox
import os
import win32print
import win32api

# Dicionário de funcionários
funcionarios = {"João da Silva": 220, "Maria Souza": 221, "Carlos Pereira": 222}

def verificar_matricula():
    matricula = entrada_matricula.get()
    try:
        matricula = int(matricula)
    except ValueError:
        messagebox.showerror("Erro", "Matrícula inválida. Por favor, insira um número.")
        return

    for nome, mat in funcionarios.items():
        if mat == matricula:
            confirmar_impressao(nome, matricula)
            return

    messagebox.showerror("Erro", "Matrícula não encontrada.")

def confirmar_impressao(nome, matricula):
    janela_confirmacao = tk.Toplevel(root)
    janela_confirmacao.title("Confirmação")

    label_confirmacao = tk.Label(janela_confirmacao, text=f"Você é {nome}?")
    label_confirmacao.pack()

    botao_sim = tk.Button(janela_confirmacao, text="SIM", command=lambda: imprimir_pdf(matricula))
    botao_sim.pack(side=tk.LEFT, padx=10)

    botao_nao = tk.Button(janela_confirmacao, text="NÃO", command=janela_confirmacao.destroy)
    botao_nao.pack(side=tk.RIGHT, padx=10)

def imprimir_pdf(matricula):
    pdf_file = f"{matricula}.pdf"
    if os.path.isfile(pdf_file):
        try:
            # Nome da impressora física
            printer_name = "HP DeskJet 2700 series"
            
            # Configurar e abrir a impressora
            printer_handle = win32print.OpenPrinter(printer_name)
            job_info = win32print.StartDocPrinter(printer_handle, 1, ("Impressão de PDF", None, "RAW"))
            win32print.StartPagePrinter(printer_handle)

            # Ler o conteúdo do arquivo PDF
            with open(pdf_file, "rb") as pdf_file_handle:
                pdf_data = pdf_file_handle.read()

            # Enviar dados do PDF para a impressora
            win32print.WritePrinter(printer_handle, pdf_data)
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)

            messagebox.showinfo("Sucesso", "PDF enviado para impressão.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar PDF para impressão: {e}")
    else:
        messagebox.showerror("Erro", f"Arquivo {pdf_file} não encontrado.")

root = tk.Tk()
root.title("Controle de Ponto")

label_matricula = tk.Label(root, text="Digite sua matrícula:")
label_matricula.pack(pady=5)

entrada_matricula = tk.Entry(root)
entrada_matricula.pack(pady=5)

botao_verificar = tk.Button(root, text="Verificar", command=verificar_matricula)
botao_verificar.pack(pady=20)

root.mainloop()
