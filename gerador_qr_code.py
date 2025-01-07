import json
import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog

import qrcode
from PIL import Image, ImageTk, ImageColor
from io import BytesIO

default_box_size, default_border = 10, 4


def main():
    pass


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
        imagem_com_logo = adicionar_imagem_no_meio(img, entrada_logo.get())
        if imagem_com_logo:
            img = imagem_com_logo
        if img:
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
                text=f'Dimensões da imagem: {largura}x{altura} px    Tamanho \
                da imagem: {tamanho_arquivo} bytes')
        else:
            preview_label.config(image='')


def update_presets():
    pass


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
    image = filedialog.askopenfile(defaultextension=".png", filetypes
    =formatos)
    if image:
        entrada_logo.config(state=tk.NORMAL)
        entrada_logo.delete(0, tk.END)
        entrada_logo.insert(0, image.name)
        entrada_logo.config(state=tk.DISABLED)
        atualizar_preview()
        return Image.open(image.name)
    else:
        entrada_logo.delete(0, tk.END)
        return ""


def salvar_qr_code(img):
    formatos = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg"),
        ("BMP files", "*.bmp")
    ]
    arquivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes
    =formatos)
    if arquivo:
        if arquivo.endswith('.jpg') or arquivo.endswith('.jpeg'):
            img = img.convert("RGB")
        img.save(arquivo)
        messagebox.showinfo("Sucesso", f"QR Code salvo como '{arquivo}'")


def salvar_json():
    caminho = filedialog.asksaveasfilename(defaultextension=".json", filetypes
    =[("JSON files", "*.json")])
    if caminho:
        with open(caminho, 'w') as arquivo:
            json.dump(
                {
                    "texto": entrada.get(),
                    "cor": entrada_cor.get(),
                    "logo": entrada_logo.get()
                },
                arquivo,
                indent=4
            )


def carregar_json():
    caminho = filedialog.askopenfilename(defaultextension=".json", filetypes
    =[("JSON files", "*.json")])
    if caminho:
        with open(caminho, 'r') as arquivo:
            configuracoes = dict(json.load(arquivo))
            print(configuracoes)
        if configuracoes:
            entrada.delete(0, tk.END)
            entrada.insert(0, configuracoes['texto'])
            entrada_cor.config(state=tk.NORMAL)
            entrada_cor.delete(0, tk.END)
            entrada_cor.insert(0, configuracoes['cor'])
            entrada_cor.config(state=tk.DISABLED)
            entrada_logo.config(state=tk.NORMAL)
            entrada_logo.delete(0, tk.END)
            entrada_logo.insert(0, configuracoes['logo'])
            entrada_logo.config(state=tk.DISABLED)
            atualizar_preview()


def adicionar_imagem_no_meio(img, logo):
    try:
        if logo and logo != "":
            logo = Image.open(logo)
            logo.convert("RGBA")
            logo.convert("RGB")
            largura_logo, altura_logo = logo.size
            largura_qr, altura_qr = img.size
            """
            Redimensiona a imagem do logo se for maior que 1/6 do
            tamanho do QR Code
            """
            fator_redimensionamento = min(largura_qr // 6 / largura_logo, altura_qr
                                          // 6 / altura_logo)
            if fator_redimensionamento < 1:
                logo = logo.resize((int(largura_logo * fator_redimensionamento), int(
                    altura_logo * fator_redimensionamento)), Image.LANCZOS)
            largura_logo, altura_logo = logo.size
            posicao = ((largura_qr - largura_logo) // 2, (altura_qr - altura_logo
                                                          ) // 2)
            img.paste(logo, posicao, logo)
            return img
    except (FileNotFoundError, PermissionError):
        pass


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
        if entrada_logo.get():
            img = adicionar_imagem_no_meio(img, entrada_logo.get())
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
entrada.bind("<KeyRelease>", lambda _: atualizar_preview())
# Cor do QR Code
botao_cor = tk.Button(janela, text="Escolher cor", command=escolher_cor)
botao_cor.pack(pady=10)

entrada_cor = tk.Entry(janela, width=40, state=tk.DISABLED)
entrada_cor.pack(pady=10)
# Imagem do meio do QR Code
botao_logo = tk.Button(janela, text="Escolher logo", command=escolher_logo)
botao_logo.pack(pady=10)

entrada_logo = tk.Entry(janela, width=40, state=tk.DISABLED)
entrada_logo.pack(pady=10)

box_size = tk.Entry(janela, width=20, state=tk.DISABLED)
box_size.pack(pady=5)
# box_size.bind("<FocusOut>", lambda _: update_presets())
# box_size=10,
# border=4,

rotulo_salvar_json = tk.Label(janela, text="Salvar as configurações em um arquivo JSON")
rotulo_salvar_json.pack(pady=10)
botao_salvar_json = tk.Button(janela, text="Salvar JSON", command=salvar_json)
botao_salvar_json.pack(pady=10)

rotulo_carregar_json = tk.Label(janela, text="Carregar as configurações de um arquivo JSON")
rotulo_carregar_json.pack(pady=10)
botao_carregar_json = tk.Button(janela, text="Carregar JSON", command=carregar_json)
botao_carregar_json.pack(pady=10)

# Preview do QR Code
preview_label = tk.Label(janela)
preview_label.pack(pady=10)

preview_info = tk.Label(janela)
preview_info.pack(pady=10)
# Botão para guardar o QR Code
botao_salvar = tk.Button(janela, text="Guardar QR Code", command=generate_qr_code)
botao_salvar.pack(pady=10)

janela.mainloop()
