import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog

import qrcode
from PIL import Image, ImageTk, ImageColor
from io import BytesIO


def main():
    ...


def atualizar_preview():
    dados = entrada.get()
    cor = verificar_cor(entrada_cor.get()) or 'black'
    if dados:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(dados)
        qr.make(fit=True)
        img = qr.make_image(fill_color=cor, back_color='white')
        img = img.convert("RGBA")
        if local_logo.get():
            img = adicionar_imagem_no_meio(img, local_logo.get())
        largura, altura = img.size
        largura_fixa = 250
        altura_fixa = 250
        img = img.resize((largura_fixa, altura_fixa), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        preview_label.config(image=img_tk)
        preview_label.image = img_tk

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        tamanho_arquivo = buffer.tell()
        preview_info.config(
            text=f'Dimensões da imagem: {largura}x{altura} px    Tamanho da imagem: {tamanho_arquivo} bytes')
    else:
        preview_label.config(image='')


def escolher_cor():
    cor = colorchooser.askcolor()[1]
    if cor:
        entrada_cor.config(state=tk.NORMAL)
        entrada_cor.delete(0, tk.END)
        entrada_cor.insert(0, cor)
        entrada_cor.config(state=tk.DISABLED)
        atualizar_preview()


def verificar_cor(cor):
    try:
        ImageColor.getrgb(cor)
        return cor
    except ValueError:
        return None


def escolher_logo():
    formatos = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg"),
        ("BMP files", "*.bmp")
    ]
    image = filedialog.askopenfile(defaultextension=".png", filetypes \
        =formatos)
    if image:
        local_logo.config(state=tk.NORMAL)
        local_logo.delete(0, tk.END)
        local_logo.insert(0, image.name)
        local_logo.config(state=tk.DISABLED)
        atualizar_preview()
        return Image.open(image.name)
    else:
        local_logo.delete(0, tk.END)
        return ""


def salvar_qr_code(img):
    formatos = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg"),
        ("BMP files", "*.bmp")
    ]
    arquivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes \
        =formatos)
    if arquivo:
        if arquivo.endswith('.jpg') or arquivo.endswith('.jpeg'):
            img = img.convert("RGB")
        img.save(arquivo)
        messagebox.showinfo("Sucesso", f"QR Code salvo como '{arquivo}'")


def adicionar_imagem_no_meio(img, logo):
    logo = Image.open(logo).convert("RGBA")
    logo.convert("RGB")
    largura_logo, altura_logo = logo.size
    largura_qr, altura_qr = img.size
    # Redimensionar a imagem do logo se for maior que 1/6 do tamanho do QR Code
    fator_redimensionamento = min(largura_qr // 6 / largura_logo, altura_qr \
                                  // 6 / altura_logo)
    if fator_redimensionamento < 1:
        logo = logo.resize((int(largura_logo * fator_redimensionamento), int(
            altura_logo * fator_redimensionamento)), Image.LANCZOS)
    largura_logo, altura_logo = logo.size
    posicao = ((largura_qr - largura_logo) // 2, (altura_qr - altura_logo
                                                  ) // 2)
    mask = logo.split()[3]
    img.paste(logo, posicao, logo)
    return img


def generate_qr_code():
    dados = entrada.get()
    cor = verificar_cor(entrada_cor.get()) or 'black'
    if dados:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(dados)
        qr.make(fit=True)
        img = qr.make_image(fill_color=cor, back_color='white')
        img = img.convert("RGBA")
        if local_logo.get():
            img = adicionar_imagem_no_meio(img, local_logo.get())
        salvar_qr_code(img)
    else:
        messagebox.showwarning("Aviso", "Por favor, insira algum texto para g\
erar o QR Code")


# Cria a janela principal
janela = tk.Tk()
janela.title("Gerador de QR Code")
# Texto do QR Code
rotulo = tk.Label(janela, text="Insira o texto para gerar o QR Code:")
rotulo.pack(pady=5)

entrada = tk.Entry(janela, width=40)
entrada.pack(pady=10)
entrada.bind("<KeyRelease>", lambda event: atualizar_preview())
# Cor do QR Code
botao_cor = tk.Button(janela, text="Escolher cor", command=escolher_cor)
botao_cor.pack(pady=10)

entrada_cor = tk.Entry(janela, width=40, state=tk.DISABLED)
entrada_cor.pack(pady=10)
# Imagem do meio do QR Code
botao_logo = tk.Button(janela, text="Escolher logo", command=escolher_logo)
botao_logo.pack(pady=10)

local_logo = tk.Entry(janela, width=40, state=tk.DISABLED)
local_logo.pack(pady=10)

preview_label = tk.Label(janela)
preview_label.pack(pady=10)

preview_info = tk.Label(janela)
preview_info.pack(pady=10)
# Botão para guardar o QR Code
botao = tk.Button(janela, text="Guardar QR Code", command=generate_qr_code)
botao.pack(pady=10)

janela.mainloop()
