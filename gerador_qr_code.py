import json
import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog, ttk
from tkinter import *
from tkinter.messagebox import showinfo

import qrcode
from PIL import Image, ImageTk, ImageColor
from io import BytesIO

DEFAULT_BOX_SIZE, DEFAULT_BORDER = 10, 4
MAX_SIZE_PREVIEW = 290


# Corrigir interface
def main():
    pass


def open_historic_window(file):
    if file:
        file = sorted(dict(json.load(file)).items())[0:100]
        file = sorted(file, key=lambda qr_code: qr_code[1]['data'])
        print(file)
    janela_historico = Toplevel()
    janela_historico.title("Histórico de QR Codes gerados")
    janela_historico.config(width=500, height=400)

    scrollbar = ttk.Scrollbar(janela_historico)
    scrollbar.pack(side=RIGHT, fill=Y)
    scrollbar_h = ttk.Scrollbar(janela_historico, orient=HORIZONTAL)
    scrollbar_h.pack(side=BOTTOM, fill=X)

    columns = ('qr_code_image', 'file', 'data', 'archive_size')
    tree_frame = Frame(janela_historico, bg="black")
    tree_frame.pack(expand=TRUE, fill=BOTH)
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
    tree.heading('qr_code_image', text='QR Code')
    tree.heading('file', text='Caminho')
    tree.heading('data', text='Data de salvamento')
    tree.heading('archive_size', text='Tamanho(bytes)')
    tree.column('qr_code_image', width=50, anchor=CENTER)
    tree.column('file', width=150, anchor=tk.W)
    tree.column('data', width=100, anchor=tk.W)
    tree.column('archive_size', width=100, anchor=tk.W)

    # generate sample data
    contacts = []
    for qr_code_data in file:
        file_path = qr_code_data[1]['file'] if qr_code_data[1].get('file') else None
        try:
            miniature = Image.open(file_path) if file_path else ""
        except PermissionError:
            miniature = ""
        contacts.append((miniature, f'last {1}', f'email{1}@example.com'))

    # add data to the treeview
    for contact in contacts:
        tree.insert('', tk.END, values=contact)

    def item_selected(event):
        for selected_item in tree.selection():
            item = tree.item(selected_item)
            record = item['values']
            # show a message
            showinfo(title='Information', message=','.join(record))

    tree.bind('<<TreeviewSelect>>', item_selected)

    tree.pack(fill=BOTH, expand=TRUE)
    # add two scrollbars
    tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)
    scrollbar.config(command=tree.yview)
    scrollbar_h.config(command=tree.xview)

def atualizar_preview():
    img = generate_qr_code()
    if entrada_logo.get():
        img = adicionar_imagem_no_meio(img, entrada_logo.get())
    if img:
        largura, altura = img.size
        if largura > MAX_SIZE_PREVIEW and altura > MAX_SIZE_PREVIEW:
            img = img.resize((MAX_SIZE_PREVIEW, MAX_SIZE_PREVIEW), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        preview_image.config(image=img_tk)
        preview_image.image = img_tk

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        tamanho_arquivo = buffer.tell()
        botao_salvar.config(state=tk.NORMAL)
        preview_info.config(
            text=f'Dimensões da imagem(ao salvar): {largura}x{altura} px    Tamanho \
da imagem: {tamanho_arquivo} bytes')
    else:
        botao_salvar.config(state=tk.DISABLED)
        preview_image.config(image='')
        preview_info.config(text="")


def confirm_preset(entry, config):
    if entry.get():
        value = entry.get()
        match config:
            case "boxSize":
                if value != "":
                    if value.isnumeric():
                        value = int(value)
                        if 10 >= value >= 1:
                            return value
                else:
                    return DEFAULT_BOX_SIZE
            case "border":
                if value != "":
                    if value.isnumeric():
                        value = int(value)
                        if 4 >= value >= 0:
                            return value
                else:
                    return DEFAULT_BORDER
            case _:
                pass


def escolher_cor():
    cor = colorchooser.askcolor()[1]
    if cor:
        entrada_cor.config(state=tk.NORMAL)
        entrada_cor.delete(0, tk.END)
        entrada_cor.insert(0, cor)
        entrada_cor.config(state=tk.DISABLED)
        atualizar_preview()


def atualizar_entrada(entry, task, value="", upd_tk=False, disable=False):
    if entry:
        if task == "update":
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, value if value or value == 0 else value)

        elif task == "delete":
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
        if disable:
            entry.config(state=tk.DISABLED)
        if upd_tk:
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


def generate_qr_code():
    dados = entrada_qr.get()
    cor = verificar_cor(entrada_cor.get()) or 'black'
    if dados:
        border = confirm_preset(entrada_border, "border")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=confirm_preset(entrada_box_size, "boxSize") or DEFAULT_BOX_SIZE,
            border=border if border or border == 0 else DEFAULT_BORDER
        )
        qr.add_data(dados)
        qr.make(fit=True)
        img = qr.make_image(fill_color=cor, back_color='white')
        if entrada_logo.get():
            img = adicionar_imagem_no_meio(img, entrada_logo.get())
        return img


def salvar_qr_code():
    formatos = [
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg"),
        ("BMP files", "*.bmp")
    ]
    img = generate_qr_code()
    if img:
        arquivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes
        =formatos)
        if arquivo:
            if arquivo.endswith('.jpg') or arquivo.endswith('.jpeg'):
                pass
            img.save(arquivo)
            messagebox.showinfo("Sucesso", f"QR Code salvo como '{arquivo}'")


def salvar_json():
    caminho = filedialog.asksaveasfilename(defaultextension=".json", filetypes
    =[("JSON files", "*.json")])
    if caminho:
        with open(caminho, 'w') as arquivo:
            json.dump(
                {
                    "texto": entrada_qr.get(),
                    "cor": entrada_cor.get(),
                    "logo": entrada_logo.get(),
                    "box size": entrada_box_size.get(),
                    "border": entrada_border.get()
                },
                arquivo,
                indent=4
            )


def carregar_json():
    caminho = filedialog.askopenfilename(defaultextension=".json", filetypes
    =[("JSON files", "*.json")])
    default = {
        "texto": "",
        "cor": '#fff',
        "logo": "",
        "box size": "",
        "border": ""
    }
    if caminho:
        with open(caminho, 'r') as arquivo:
            configuracoes = dict(json.load(arquivo)) or default
            for key, value in default.items():
                if not configuracoes.get(key):
                    configuracoes[key] = value
            try:
                atualizar_entrada(entrada_qr, "update", configuracoes['texto'])
                atualizar_entrada(entrada_cor, "update", configuracoes['cor'], disable=True)
                atualizar_entrada(entrada_logo, "update", configuracoes['logo'], disable=True)
                atualizar_entrada(entrada_box_size, "update", configuracoes['box size'])
                atualizar_entrada(entrada_border, "update", configuracoes['border'], upd_tk=True)
            except KeyError as e:
                print("Missing key in JSON file: ", e.args)


def carregar_historico():
    with open('qr_code_historic.json', "r") as historic:
        if historic:
            open_historic_window(historic)



def adicionar_imagem_no_meio(img, logo):
    try:
        if img and logo:
            logo = Image.open(logo).convert("RGBA")
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


# Cria a janela principal
janela = Tk()
janela.title("Gerador de QR Code")
janela.geometry("800x680")
# Cria os frames principais
frame_esquerdo = Frame(janela, bg="cyan")
frame_esquerdo.pack(side=LEFT, fill=BOTH, expand=TRUE)
frame_esquerdo.pack_propagate(False)
preview = Frame(janela, bg="blue")
preview.pack(side=LEFT, fill=BOTH, expand=TRUE)
preview.pack_propagate(False)
frame_direito = Frame(janela, bg="green")
frame_direito.pack(side=LEFT, fill=BOTH, expand=TRUE)
frame_direito.pack_propagate(False)

opcoes_esquerda_principal = Frame(frame_esquerdo, bg="purple")
opcoes_esquerda_principal.pack(anchor=CENTER, expand=TRUE)

rotulo_esquerdo = Label(opcoes_esquerda_principal, text="Configurações do gerador", pady=10)
rotulo_esquerdo.pack()
# Para configurar o "box_size" do QR Code
rotulo_box_size = Label(opcoes_esquerda_principal, text="Tamanho de caixa")
rotulo_box_size.pack()
entrada_box_size = Entry(opcoes_esquerda_principal, width=10)
entrada_box_size.bind("<KeyRelease>", lambda _: atualizar_preview())
entrada_box_size.pack()
# Para configurar a "border" do QR Code
rotulo_border = Label(opcoes_esquerda_principal, text="Tamanho da borda")
rotulo_border.pack()
entrada_border = Entry(opcoes_esquerda_principal, width=10)
entrada_border.bind("<KeyRelease>", lambda _: atualizar_preview())
entrada_border.pack()
# Botão para abrir o histórico de QR Codes salvos
abrir_historico = Button(frame_esquerdo, text="Abrir histórico de QR Codes", command=carregar_historico)
abrir_historico.pack(anchor=N, expand=TRUE)
# Preview do QR Code
preview_image = Label(preview)
preview_image.pack(anchor=CENTER, expand=TRUE)
preview_max_size_info = Label(preview, text=f'Preview image max size: {MAX_SIZE_PREVIEW}x{MAX_SIZE_PREVIEW} px')
preview_max_size_info.place(anchor=CENTER, relx=0.5, rely=0.75)
preview_info = Label(janela)
preview_info.place(anchor=CENTER, relx=0.5, rely=0.8)
# Botão para guardar o QR Code
botao_salvar = Button(janela, text="Guardar QR Code", state=tk.DISABLED, command=salvar_qr_code)
botao_salvar.place(anchor=CENTER, relx=0.5, rely=0.9)
# Cria o frame de geração e carregamento da direita
opcoes_direita_principal = Frame(frame_direito, bg="pink")
opcoes_direita_principal.pack(expand=TRUE)
# Texto do QR Code
rotulo = Label(opcoes_direita_principal, text="Insira o texto para gerar o QR Code:", pady=10)
rotulo.grid(row=0)

entrada_qr = Entry(opcoes_direita_principal, width=40)
entrada_qr.bind("<KeyRelease>", lambda _: atualizar_preview())
entrada_qr.grid(row=1)
# Cor do QR Code
botao_cor = Button(opcoes_direita_principal, text="Escolher cor", command=escolher_cor)
botao_cor.grid(row=2, pady=15)

entrada_cor = Entry(opcoes_direita_principal, width=40, state=tk.DISABLED)
entrada_cor.grid(row=3)

excluir_cor = Button(opcoes_direita_principal, text="X", command=lambda entrada=entrada_cor: atualizar_entrada(entrada, "delete", upd_tk=True, disable=True))
excluir_cor.grid(row=3, column=2, ipadx=5, columnspan=2)
# Imagem do meio do QR Code
botao_logo = Button(opcoes_direita_principal, text="Escolher logo", command=escolher_logo)
botao_logo.grid(row=4, pady=15)

entrada_logo = Entry(opcoes_direita_principal, width=40, state=tk.DISABLED)
entrada_logo.grid(row=5)

excluir_logo = Button(opcoes_direita_principal, text="X", command=lambda entrada=entrada_logo: atualizar_entrada(entrada, "delete", upd_tk=True, disable=True))
excluir_logo.grid(row=5, column=2, ipadx=5, columnspan=2)
# box_size = Entry(janela, width=20, state=tk.DISABLED)
# box_size.bind("<FocusOut>", lambda _: update_presets())
# box_size=10,
# border=4,

rotulo_salvar_json = Label(opcoes_direita_principal, text="Salvar as configurações em um arquivo JSON")
rotulo_salvar_json.grid(row=6)
botao_salvar_json = Button(opcoes_direita_principal, text="Salvar JSON", command=salvar_json)
botao_salvar_json.grid(row=7, pady=7)

rotulo_carregar_json = Label(opcoes_direita_principal, text="Carregar as configurações de um arquivo JSON")
rotulo_carregar_json.grid(row=8)
botao_carregar_json = Button(opcoes_direita_principal, text="Carregar JSON", command=carregar_json)
botao_carregar_json.grid(row=9, pady=7)
# Ativa a janela do programa
janela.mainloop()
