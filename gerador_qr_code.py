import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog, ttk
from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.ttk import Combobox
import qrcode
from PIL import Image, ImageTk, ImageColor
from io import BytesIO
from qrcode.main import QRCode


# Corrigir interface
# Corrigir tamanho das linhas
# Corrigir comentários
class QRCodeGenerator:

    def __init__(self):
        self.__local_historic = None
        self._historic_reference = 'qr_code_historic.json'
        self._DEFAULT_VERSION = 1
        self._DEFAULT_BOX_SIZE, self._DEFAULT_BORDER = 10, 4
        self._VERSION_VALUES = [str(v) for v in range(1, 41)]
        self._BOX_SIZE_VALUES = [str(v) for v in range(1, 11)]
        self._BORDER_SIZE_VALUES = [str(v) for v in range(0, 5)]
        self._LOGO_SIZE_VALUES = [str(v) for v in range(1, 5)]
        self._MAX_SIZE_PREVIEW = 290
        self._max_size_historic_thumbnails = 50
        self._qr_code_logo_size = 6

        try:
            with open(self.historic_reference, 'r') as file:
                self.local_historic = dict(json.load(file))
        except (PermissionError, FileNotFoundError):
            messagebox.showwarning('Warning', 'Cannot load local historic file')

    @property
    def local_historic(self):
        return self.__local_historic

    @local_historic.setter
    def local_historic(self, historic):
        self.__local_historic = historic

    @property
    def historic_reference(self):
        return self._historic_reference

    @historic_reference.setter
    def historic_reference(self, reference):
        self._historic_reference = reference

    @property
    def default_version(self):
        return self._DEFAULT_VERSION

    @property
    def default_box_size(self):
        return self._DEFAULT_BOX_SIZE

    @property
    def default_border(self):
        return self._DEFAULT_BORDER

    @property
    def version_values(self):
        return self._VERSION_VALUES

    @property
    def box_size_values(self):
        return self._BOX_SIZE_VALUES

    @property
    def border_size_values(self):
        return self._BORDER_SIZE_VALUES

    @property
    def qr_code_logo_size_values(self):
        return self._LOGO_SIZE_VALUES

    @property
    def qr_code_logo_size(self):
        return self._qr_code_logo_size

    @qr_code_logo_size.setter
    def qr_code_logo_size(self, size):
        self.qr_code_logo_size = size

    @property
    def max_size_preview(self):
        return self._MAX_SIZE_PREVIEW

    @property
    def max_size_historic_thumbnails(self):
        return self._max_size_historic_thumbnails

    @max_size_historic_thumbnails.setter
    def max_size_historic_thumbnails(self, size):
        self.max_size_historic_thumbnails = size

    def atualizar_preview(self):
        img = self.generate_qr_code()
        if qr_code_logo_entry.get():
            img = adicionar_imagem_no_meio(img, qr_code_logo_entry.get())
        if img:
            largura, altura = img.size
            if largura > self._MAX_SIZE_PREVIEW and altura > self._MAX_SIZE_PREVIEW:
                img = img.resize((self._MAX_SIZE_PREVIEW, self._MAX_SIZE_PREVIEW), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            preview_image.config(image=img_tk)
            preview_image.image = img_tk

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            tamanho_arquivo = buffer.tell()
            save_qr_code_button.config(state=tk.NORMAL)
            preview_info.config(
                text=f'Dimensões da imagem(ao salvar): {largura}x{altura} px    Tamanho \
    da imagem: {tamanho_arquivo} bytes')
        else:
            save_qr_code_button.config(state=tk.DISABLED)
            preview_image.config(image='')
            preview_info.config(text="")

    def confirm_preset(self, entry, config):
        if entry.get():
            value = entry.get()
            match config:
                case "version":
                    if value != "":
                        if value.isnumeric():
                            value = int(value)
                            if 40 >= value >= 1:
                                return value
                    else:
                        return self.default_version
                case "boxSize":
                    if value != "":
                        if value.isnumeric():
                            value = int(value)
                            if 10 >= value >= 1:
                                return value
                    else:
                        return self.default_box_size
                case "border":
                    if value != "":
                        if value.isnumeric():
                            value = int(value)
                            if 4 >= value >= 0:
                                return value
                    else:
                        return self.default_border
                case _:
                    pass

    def escolher_cor(self):
        cor = colorchooser.askcolor()[1]
        if cor:
            qr_code_color_entry.config(state=tk.NORMAL)
            qr_code_color_entry.delete(0, tk.END)
            qr_code_color_entry.insert(0, cor)
            qr_code_color_entry.config(state=tk.DISABLED)
            self.atualizar_preview()

    def atualizar_entrada(self, entry, task, value="", upd_tk=False, disable=False):
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
                self.atualizar_preview()

    def set_qr_code_logo_size(self):
        self._qr_code_logo_size = int(qr_code_logo_size_entry.get()) * 2
        self.atualizar_preview()

    def escolher_logo(self):
        formatos = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("BMP files", "*.bmp")
        ]
        image = filedialog.askopenfile(defaultextension=".png", filetypes
        =formatos)
        if image:
            qr_code_logo_entry.config(state=tk.NORMAL)
            qr_code_logo_entry.delete(0, tk.END)
            qr_code_logo_entry.insert(0, image.name)
            qr_code_logo_entry.config(state=tk.DISABLED)
            self.atualizar_preview()
            return Image.open(image.name)
        else:
            qr_code_logo_entry.delete(0, tk.END)
            return ""

    def generate_qr_code(self):
        dados = qr_code_entry.get()
        cor = verificar_cor(qr_code_color_entry.get()) or 'black'
        if dados:
            version = self.confirm_preset(qr_code_version_entry, "version")
            border = self.confirm_preset(border_entry, "border")
            qr = qrcode.QRCode(
                version=version if version else self.default_version,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=self.confirm_preset(box_size_entry, "boxSize") or self.default_box_size,
                border=border if border or border == 0 else self.default_border
            )
            qr.add_data(dados)
            qr.make(fit=True)
            img = qr.make_image(fill_color=cor, back_color='white')
            if qr_code_logo_entry.get():
                img = adicionar_imagem_no_meio(img, qr_code_logo_entry.get())
            return img

    def salvar_qr_code(self):
        formatos = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("BMP files", "*.bmp")
        ]
        img = self.generate_qr_code()
        if img:
            arquivo = filedialog.asksaveasfilename(defaultextension=".png", filetypes
            =formatos)
            if arquivo:
                if arquivo.endswith('.jpg') or arquivo.endswith('.jpeg'):
                    img = convert_image(img, "RGBA", "RGB")
                else:
                    pass
                img.save(arquivo, quality=100)

                qr_code_save_info = {
                        'data': qr_code_entry.get(),
                        'date': str(datetime.today()),
                        'logo': qr_code_logo_entry.get(),
                        'color': qr_code_color_entry.get(),
                        'boxSize': box_size_entry.get()
                    }

                if not self.local_historic.get(arquivo):
                    self.local_historic.setdefault(arquivo, qr_code_save_info)
                else:
                    self.local_historic[arquivo] = qr_code_save_info


                try:
                    with open(self.historic_reference, 'w') as file:
                        file.write(json.dumps(self.local_historic, indent=4))

                except (PermissionError, FileNotFoundError):
                    pass
                messagebox.showinfo("Sucesso", f"QR Code salvo como '{arquivo}'")

    def carregar_json(self):
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
                    self.atualizar_entrada(qr_code_entry, "update", configuracoes['texto'])
                    self.atualizar_entrada(qr_code_color_entry, "update", configuracoes['cor'], disable=True)
                    self.atualizar_entrada(qr_code_logo_entry, "update", configuracoes['logo'], disable=True)
                    self.atualizar_entrada(box_size_entry, "update", configuracoes['box size'])
                    self.atualizar_entrada(border_size_entry, "update", configuracoes['border'], upd_tk=True)
                except KeyError as e:
                    print("Missing key in JSON file: ", e.args)


class Historic(QRCodeGenerator):

    def __init__(self, file):
        super().__init__()
        self.__file = file
        if type(self.__file) == dict:
            file = sorted(file.items())[0:100]
            file = sorted(file, key=lambda qr_code: qr_code[1]['date'] if qr_code[1].get('date') else qr_code[0], reverse=True)
            window = Toplevel()
            window.title("Histórico de QR Codes gerados")
            window.config(width=500, height=400)

            scrollbar = ttk.Scrollbar(window)
            scrollbar.pack(side=RIGHT, fill=Y)
            scrollbar_h = ttk.Scrollbar(window, orient=HORIZONTAL)
            scrollbar_h.pack(side=BOTTOM, fill=X)

            columns = ('file', 'date', 'archive_size')
            style = ttk.Style()
            style.configure('Treeview', rowheight=100)
            tree_frame = Frame(window, bg="white")
            tree_frame.pack(expand=TRUE, fill=BOTH)
            tree = ttk.Treeview(tree_frame, selectmode='browse', columns=columns)
            tree.heading('#0', text='QR Code', anchor=CENTER)
            tree.heading('file', text='Caminho', anchor=CENTER)
            tree.heading('date', text='Data de salvamento', anchor=CENTER)
            tree.heading('archive_size', text='Tamanho(bytes)', anchor=CENTER)
            tree.column('#0', width=100)
            tree.column('file', anchor=CENTER)
            tree.column('date', anchor=CENTER)
            tree.column('archive_size', anchor=CENTER)
            # generate data
            qr_codes = []
            if file:
                for qr_code_data in file:
                    miniature_size = 0
                    file_path = qr_code_data[0] or None
                    try:
                        with Image.open(file_path) as qr_code_image:
                            qr_code_image.thumbnail(
                                (self.max_size_historic_thumbnails, self.max_size_historic_thumbnails))
                            miniature = ImageTk.PhotoImage(qr_code_image)
                            qr_codes.append(miniature)
                            if qr_code_image:
                                buffer = BytesIO()
                                qr_code_image.save(buffer, "PNG")
                                miniature_size = buffer.tell()
                    except (PermissionError, FileNotFoundError):
                        miniature = None
                    tree.insert("", 'end', open=True, image=miniature or "", text=qr_code_data[0][qr_code_data[0].find('.') + 1:len(qr_code_data[0])], values=(
                        f'{file_path}',
                        f'{qr_code_data[1]['date'] if qr_code_data[1].get('date') else ""}',
                        f'{miniature_size} bytes'
                    )
                                )
            tree.images = qr_codes

            def item_selected(event):
                for selected_item in tree.selection():
                    pass
                    # item = tree.item(selected_item)
                    # record = item['values']
                    # show a message
                    # showinfo(title='Information', message=','.join(record))

            tree.bind('<<TreeviewSelect>>', item_selected)

            tree.pack(fill=BOTH, expand=True)
            # add two scrollbars
            tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)
            scrollbar.config(command=tree.yview)
            scrollbar_h.config(command=tree.xview)


def main():
    pass


def open_historic_window(file):
    Historic(file)


def verificar_cor(cor):
    try:
        ImageColor.getrgb(cor)
        return cor
    except ValueError:
        return None


# Ativa a main_window do programa


def convert_image(image, image_type, convert_to):
    if image:
        allowed_types = ['RGB', 'RGBA']
        modes = ['RGB', 'RGBA']
        if image_type in modes:
            if type(convert_to) == str and convert_to in modes:
                if type(image_type) == str and image_type in allowed_types:
                    converted_image = None
                    if image_type == "RGBA" and convert_to == "RGB":
                        converted_image = Image.new('RGB', image.size)
                        for x in range(image.width):
                            for y in range(image.height):
                                r, g, b, a = image.getpixel((x, y))
                                converted_image.putpixel((x, y), (r, g, b))
                    elif image_type == "RGB" and convert_to == "RGBA":
                        converted_image = image.convert("RGBA")
                    return converted_image or image


def salvar_json():
    caminho = filedialog.asksaveasfilename(defaultextension=".json", filetypes
    =[("JSON files", "*.json")])
    if caminho:
        with open(caminho, 'w') as arquivo:
            json.dump(
                {
                    "texto": qr_code_entry.get(),
                    "cor": qr_code_color_entry.get(),
                    "logo": qr_code_logo_entry.get(),
                    "box size": box_size_entry.get(),
                    "border": qr_code_border_entry.get()
                },
                arquivo,
                indent=4
            )


def adicionar_imagem_no_meio(img, logo):
    try:
        if img and logo:
            img = img.convert("RGBA")
            logo = Image.open(logo).convert("RGBA")
            largura_logo, altura_logo = logo.size
            largura_qr, altura_qr = img.size
            """
            Redimensiona a imagem do logo se for maior que 1/6 do
            tamanho do QR Code
            """
            fator_redimensionamento = min(largura_qr // qr_code_generator.qr_code_logo_size * 2 / largura_logo, altura_qr
                                          // qr_code_generator.qr_code_logo_size * 2 / altura_logo)
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


main()

qr_code_generator = QRCodeGenerator()
# Cria a main_window principal
main_window = Tk()
main_window.title("Gerador de QR Code")
main_window.geometry("800x680")
# Cria os frames principais
# Frame esquerdo
left_frame = Frame(main_window, bg="cyan")
left_frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
left_frame.pack_propagate(False)
# Frame central
preview = Frame(main_window, bg="blue")
preview.pack(side=LEFT, fill=BOTH, expand=TRUE)
preview.pack_propagate(False)
# Frame direito
right_frame = Frame(main_window, bg="green")
right_frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
right_frame.pack_propagate(False)
main_left_frame = Frame(left_frame, bg="purple")
main_left_frame.pack(anchor=CENTER, expand=TRUE)
mlf_title = Label(main_left_frame, text="Configurações do gerador", pady=10)
mlf_title.pack()
# Para configurar a versão do QR Code
qr_code_version_label = Label(main_left_frame, text="Versão do QR Code")
qr_code_version_label.pack()
qr_code_version_entry = Combobox(main_left_frame, width=10, state="readonly", values=qr_code_generator.version_values, takefocus=qr_code_generator.atualizar_preview)
qr_code_version_entry.current(0)
qr_code_version_entry.bind("<<ComboboxSelected>>", lambda _: qr_code_generator.atualizar_preview())
qr_code_version_entry.pack()
# Para configurar o "box_size" do QR Code
box_size_label = Label(main_left_frame, text="Tamanho de caixa")
box_size_label.pack()
box_size_entry = Combobox(main_left_frame, width=10, state="readonly", values=qr_code_generator.box_size_values)
box_size_entry.current(9)
box_size_entry.bind("<<ComboboxSelected>>", lambda _: qr_code_generator.atualizar_preview())
box_size_entry.pack()
# Para configurar a "border" do QR Code
border_label = Label(main_left_frame, text="Tamanho da borda")
border_label.pack()
border_entry = Combobox(main_left_frame, width=10, state="readonly", values=qr_code_generator.border_size_values)
border_entry.current(4)
border_entry.bind("<<ComboboxSelected>>", lambda _: qr_code_generator.atualizar_preview())
border_entry.pack()
# Botão para abrir o histórico de QR Codes salvos
open_historic_button = Button(left_frame, text="Abrir histórico de QR Codes",
                              command=lambda historic=qr_code_generator.local_historic: open_historic_window(historic))
open_historic_button.pack(anchor=N, expand=TRUE)
# Preview do QR Code
preview_image = Label(preview)
preview_image.pack(anchor=CENTER, expand=TRUE)
preview_max_size_info = Label(preview,
                              text=f'Preview image max size: {qr_code_generator.max_size_preview}x{qr_code_generator.max_size_preview} px')
preview_max_size_info.place(anchor=CENTER, relx=0.5, rely=0.75)
preview_info = Label(main_window)
preview_info.place(anchor=CENTER, relx=0.5, rely=0.8)
# Botão para guardar o QR Code
save_qr_code_button = Button(main_window, text="Guardar QR Code", state=tk.DISABLED,
                             command=qr_code_generator.salvar_qr_code)
save_qr_code_button.place(anchor=CENTER, relx=0.5, rely=0.9)
# Cria o frame de geração e carregamento da direita
main_right_frame = Frame(right_frame, bg="pink")
main_right_frame.pack(expand=TRUE)
# Texto do QR Code
qr_code_entry_info = Label(main_right_frame, text="Insira o texto para gerar o QR Code:", pady=10)
qr_code_entry_info.pack()

qr_code_entry = Entry(main_right_frame, width=40)
qr_code_entry.bind("<KeyRelease>", lambda _: qr_code_generator.atualizar_preview())
qr_code_entry.pack()
# Cor do QR Code
qr_code_color_button = Button(main_right_frame, text="Escolher cor", command=qr_code_generator.escolher_cor)
qr_code_color_button.pack(pady=15)

qr_code_color_entry = Entry(main_right_frame, width=40, state=tk.DISABLED)
qr_code_color_entry.pack()

qr_code_color_delete_button = Button(main_right_frame, text="X",
                                     command=lambda entrada=qr_code_color_entry: qr_code_generator.atualizar_entrada(
                                         entrada, "delete", upd_tk=True,
                                         disable=True))
qr_code_color_delete_button.pack()
# Imagem do meio do QR Code
qr_code_logo_button = Button(main_right_frame, text="Escolher logo", command=qr_code_generator.escolher_logo)
qr_code_logo_button.pack(pady=15)

qr_code_logo_size_label = Label(main_right_frame, text="Tamanho da logo")
qr_code_logo_size_label.pack()
qr_code_logo_size_entry = Combobox(main_right_frame, width=10, state="readonly", values=qr_code_generator.qr_code_logo_size_values)
qr_code_logo_size_entry.current(3)
qr_code_logo_size_entry.bind("<<ComboboxSelected>>", lambda _: qr_code_generator.set_qr_code_logo_size())
qr_code_logo_size_entry.pack()
qr_code_logo_entry = Entry(main_right_frame, width=40, state=tk.DISABLED)
qr_code_logo_entry.pack()

qr_code_logo_delete_button = Button(main_right_frame, text="X",
                                    command=
                                    lambda entrada=qr_code_logo_entry: qr_code_generator.atualizar_entrada(entrada,
                                                                                                           "delete",
                                                                                                           upd_tk=True,
                                                                                                           disable=True))
qr_code_logo_delete_button.pack()
# box_size = Entry(main_window, width=20, state=tk.DISABLED)
# box_size.bind("<FocusOut>", lambda _: update_presets())
# box_size=10,
# border=4,

json_save_label = Label(main_right_frame, text="Salvar as configurações em um arquivo JSON")
json_save_label.pack()
json_save_button = Button(main_right_frame, text="Salvar JSON", command=salvar_json)
json_save_button.pack()

json_load_label = Label(main_right_frame, text="Carregar as configurações de um arquivo JSON")
json_load_label.pack()
json_load_button = Button(main_right_frame, text="Carregar JSON", command=qr_code_generator.carregar_json)
json_load_button.pack()

main_window.mainloop()
