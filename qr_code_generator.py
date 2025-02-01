import json
from datetime import datetime
from numpy import arange
import tkinter
from json import JSONDecodeError
from tkinter import messagebox, colorchooser, filedialog, ttk
from tkinter import *
from tkinter.ttk import Combobox, Treeview, Style
import qrcode
from PIL import Image, ImageTk, ImageColor
from io import BytesIO
from os import path
import configparser

# Corrigir interface
# Corrigir tamanho das linhas
# Corrigir comentários
# Corrigir linguagem
# Mudar os espaçamentos

class App(Tk):

    def __init__(self):
        super().__init__()
        self.historic_window = None  # Create a variable for the Historic object when instantiated
        self.__local_historic = None  # Create a local QR Codes historic variable for the program
        self.config_path = 'config.ini'  # Path for the app configurations file
        self.config_file = configparser.ConfigParser()
        self.config_file.read('config.ini')
        # Historic path for the main QR Codes historic
        self.historic_path = self.config_file.get('General', 'historic_path') or None
        self._DEFAULT_VERSION = 1  # Default version for the QR Code
        self._DEFAULT_BOX_SIZE, self._DEFAULT_BORDER = 10, 4  # Default box size and border for the QR Code generator
        self._VERSION_VALUES = [str(v) for v in range(1, 41)]  # Create allowed values for the version Combobox
        self._BOX_SIZE_VALUES = [str(v) for v in range(1, 11)]  # Create allowed values for the box size Combobox
        self._BORDER_SIZE_VALUES = [str(v) for v in range(0, 5)]  # Create allowed values for the border size Combobox
        # Create allowed values for the logo size Combobox
        self._LOGO_SIZE_VALUES = []
        for v in arange(0.1, 1.1, 0.1):
            v = int(v) if v % 1 == 0 or v >= 1 else round(v, 1)
            self._LOGO_SIZE_VALUES.append(str(v))
        self._MAX_SIZE_PREVIEW = 290  # QR Code image self.preview max size
        self._max_size_historic_thumbnails = 50  # Max size for the historic thumbnails
        self._qr_code_logo_size = StringVar(value='0.2')  # Default value for the QR Code logo size
        self.rr_flag = StringVar(value='1')
        self.rar_flag = StringVar(value='1')
        # Commands for get values from GUI
        self.data_commands = {'data': (lambda: self.qr_code_entry,
                                       lambda: self.qr_code_entry.get(),
                                       ''),
                              'date': (None, lambda: str(datetime.now())
                              [0:19],
                                       lambda: str(datetime.now()))[0:19],
                              'logo': (lambda: self.qr_code_logo_entry,
                                       lambda: self.qr_code_logo_entry.get(),
                                       ''),
                              'logo_size': (lambda: self._qr_code_logo_size,
                                            lambda: self._qr_code_logo_size
                                            .get(),
                                            0.2),
                              'color': (lambda: self.qr_code_color_entry,
                                        lambda: self.qr_code_color_entry
                                        .get(),
                                        ''),
                              'version': (lambda: self.qr_code_version_entry,
                                          lambda: self.qr_code_version_entry
                                          .get(),
                                          '1'),
                              'box_size': (lambda: self.box_size_entry,
                                           lambda: self.box_size_entry.get(),
                                           self.default_box_size),
                              'border': (lambda: self.border_entry,
                                         lambda: self.border_entry.get(),
                                         self.default_border),
                              'background_color': (lambda: self
                                                   .bg_color_entry,
                                                   lambda: self
                                                   .bg_color_entry
                                                   .get(),
                                                   ''),
                              'logo_aspect_ratio': (lambda: self.rar_flag,
                                                    lambda: self.rar_flag.get(),
                                                    1),
                              'resize_logo': (lambda: self.rr_flag,
                                              lambda: self.rr_flag.get(),
                                              1)
                              }
        self.set_configurations()  # Get all configurations
        # Tries to open the QR Codes historic file
        try:
            with open(self.historic_path or "", 'r', newline='\n') as file:
                try:
                    self.local_historic = dict(json.load(file))
                except JSONDecodeError:
                    self.local_historic = {}
        except (PermissionError, FileNotFoundError):
            messagebox.showwarning('Warning',
                                   'Cannot load local historic file')
        # Widgets list
        self.widgets = []
        # Ttk Style
        self.style = ttk.Style(self)
        # Window options Menu
        self.options_menu = Menu(self, tearoff=0)
        self.selected_option = StringVar()
        self.selected_option.trace('w', self.menu_item_selected)  # def
        self.menu_options = (
            'Save QR Code',
            'Open as JSON file',
            'Save as JSON file',
            'Change widgets theme',
            'Historic',
            'Reset generator configurations')
        for option in self.menu_options:
            self.options_menu.add_radiobutton(
                label=option,
                value=option,
                variable=self.selected_option,
                indicatoron=False
            )
        self.configure(menu=self.options_menu)
        # Main frames
        # Center Frame
        self.center_frame = Frame(self)
        self.center_frame.pack(fill=BOTH, expand=TRUE)
        # Center main left frame
        self.left_frame = Frame(self.center_frame)
        self.left_frame.pack(side=LEFT, expand=TRUE, fill=BOTH)
        # Center main center frame
        self.preview = Frame(self.center_frame)
        self.preview.pack(side=LEFT, expand=TRUE, fill=BOTH, ipadx=60)
        # Center main right frame
        self.right_frame = Frame(self.center_frame)
        self.right_frame.pack(side=LEFT, expand=TRUE, fill=BOTH)
        self.left_configurations_frame_1 = Frame(self.left_frame)
        self.right_configurations_frame_1 = Frame(self.right_frame)
        # QR Code version widgets
        self.qr_code_version_frame = LabelFrame(self
                                                .left_configurations_frame_1,
                                                text="Versão do QR Code")

        self.qr_code_version_entry = Combobox(self.qr_code_version_frame,
                                              width=10, state="readonly",
                                              values=self.version_values,
                                              takefocus=self.update_preview)
        self.qr_code_version_entry.current(0)
        self.qr_code_version_entry.bind("<<ComboboxSelected>>",
                                        lambda _: self.update_preview())
        # QR Code box size widgets
        self.box_size_frame = LabelFrame(self.left_configurations_frame_1,
                                         text="Tamanho de caixa")
        self.box_size_entry = Combobox(self.box_size_frame, width=10,
                                       state="readonly",
                                       values=self.box_size_values)
        self.box_size_entry.current(9)
        self.box_size_entry.bind("<<ComboboxSelected>>",
                                 lambda _: self.update_preview())
        # QR Code border widgets
        self.border_frame = LabelFrame(self.left_configurations_frame_1,
                                       text="Tamanho da borda")
        self.border_entry = Combobox(self.border_frame, width=10,
                                     state="readonly",
                                     values=self.border_size_values)
        self.border_entry.current(4)
        self.border_entry.bind("<<ComboboxSelected>>",
                               lambda _: self.update_preview())
        # QR Code background color widgets
        self.bg_frame = LabelFrame(self.left_configurations_frame_1,
                                   text="Cor de fundo do QR Code")
        self.bg_color_button = Button(self.bg_frame,
                                      text="Escolher cor")
        self.bg_color_entry = Entry(self.bg_frame,
                                    state=DISABLED, width=40)
        self.bg_color_button.configure(command=lambda color=self
        .bg_color_entry:
        choose_color(color, True))
        self.bg_color_entry.pack_propagate(False)
        self.bg_color_delete_button = Button(self.bg_frame, height=1,
                                             text="Deletar cor de fundo",
                                             command=lambda
                                                 entry=
                                                 self
                                                 .bg_color_entry:
                                             self.update_entries(
                                                 entry, "delete",
                                                 upd_preview=True,
                                                 disable=True))
        # QR Code logo checkboxes
        self.checkbox_frame = LabelFrame(self.left_configurations_frame_1,
                                         text='Logo image configurations')
        self.logo_image_aspect_ratio_flag = Checkbutton(self.checkbox_frame,
                                                        text=
                                                        "Logo aspect ratio",
                                                        variable=self
                                                        .rar_flag,
                                                        command=self
                                                        .update_preview)
        self.logo_image_resize_flag = Checkbutton(self.checkbox_frame,
                                                  text="Resize the logo",
                                                  variable=self.rr_flag,
                                                  command=self.update_preview)

        # QR Code preview widgets
        self.preview_qr_code_frame = Frame(self.preview)
        self.preview_image_frame = Frame(self.preview_qr_code_frame,
                                         width=self.max_size_preview,
                                         height=self.max_size_preview,
                                         bg='light grey',
                                         )

        self.preview_image = Label(self.preview_image_frame, anchor=CENTER,
                                   bg='light grey')
        self.preview_max_size_info = Label(self.preview_qr_code_frame,
                                           text=f'Preview image max size: '
                                                f'{self.max_size_preview}x'
                                                f'{self.max_size_preview} px')
        self.preview_info = Label(self.preview_qr_code_frame)
        self.preview_image_frame.pack_propagate(False)
        # QR Code text widgets
        self.qr_code_entry_frame = Frame(self.preview_qr_code_frame)
        self.qr_code_entry_label = Label(self.qr_code_entry_frame,
                                         text='Insert the data to '
                                              'generate the QR Code:')
        self.qr_code_entry = Entry(self.qr_code_entry_frame, width=75)
        self.qr_code_entry.bind("<KeyRelease>",
                                lambda _: self.update_preview())
        # QR Code color widgets
        self.qr_code_color_frame = LabelFrame(self
                                              .right_configurations_frame_1,
                                              text="QR Code color")
        self.qr_code_color_button = Button(self.qr_code_color_frame,
                                           text="Escolher cor")
        self.qr_code_color_entry = Entry(self.qr_code_color_frame, width=40,
                                         state=DISABLED)
        self.qr_code_color_button.configure(command=
                                            lambda color=
                                                   self.qr_code_color_entry:
                                            choose_color(color, True))
        self.qr_code_color_delete_button = Button(
            self.qr_code_color_frame, text="Deletar cor",
            command=
            lambda entry=
                   self
                   .qr_code_color_entry:
            self.update_entries(
                entry, "delete",
                upd_preview=True,
                disable=True))
        # QR Code logo widgets
        self.qr_code_logo_frame = LabelFrame(self
                                             .right_configurations_frame_1,
                                             text="QR Code logo")
        self.qr_code_logo_button = Button(self.qr_code_logo_frame,
                                          text="Escolher logo",
                                          command=self.choose_logo)
        self.qr_code_logo_entry = Entry(self.qr_code_logo_frame,
                                        width=40, state=DISABLED)
        self.qr_code_logo_delete_button = Button(self.qr_code_logo_frame,
                                                 text="Deletar logo",
                                                 command=lambda entry=self.qr_code_logo_entry: self.update_entries(
                                                     entry, "delete", upd_preview=True, disable=True))

        self.qr_code_logo_size_label = Label(self.qr_code_logo_frame,
                                             text="Tamanho da logo")
        self.qr_code_logo_size_entry = Spinbox(self.qr_code_logo_frame,
                                               width=10, state="readonly",
                                               from_=0.1,
                                               to=1,
                                               increment=0.1,
                                               textvariable=
                                               self._qr_code_logo_size,
                                               command=self.update_preview
                                               )
        for item in self.__dict__.values():
            if getattr(item, '__module__', None) in [tkinter.__name__, ttk.__name__]:
                self.widgets.append(item)
        self.widgets_defaults_configurations = {'frame': [self.center_frame.cget('background')],
                                                'button': [self.bg_color_button.cget('background'),
                                                           self.bg_color_button.cget('activebackground'),
                                                           self.bg_color_button.cget('foreground'),
                                                           self.bg_color_button.cget('activeforeground')
                                                           ],
                                                'labelFrame': [self.qr_code_color_frame.cget('background'),
                                                               self.qr_code_color_frame.cget('foreground')]
                                                }
        configure_widgets(self.widgets, self.config_file, self.widgets_defaults_configurations)
        self.widgets.remove(self.preview_image)
        for widget in self.widgets:
            if not getattr(widget, '__class__', None) in [Menu, StringVar, Style]:
                widget.pack()
            if not getattr(widget, '__class__', None) in [Label,
                                                          LabelFrame,
                                                          Frame,
                                                          StringVar,
                                                          Menu,
                                                          Checkbutton,
                                                          Style]:
                if getattr(widget, '__class__', None) == Entry:
                    widget.pack_configure(padx=10)
                widget.pack_configure(pady=(5, 15), anchor=CENTER)
            elif getattr(widget, '__class__', None) == LabelFrame:
                widget.pack_configure(fill=X)
        self.preview.configure()
        self.left_frame.configure()
        self.left_configurations_frame_1.pack(expand=TRUE)
        self.preview_qr_code_frame.pack_configure(expand=TRUE)
        self.preview_image_frame.pack_configure(pady=(50, 0))
        self.preview_image.pack_configure(expand=TRUE)
        self.preview_max_size_info.pack_configure(pady=(25, 0))
        self.preview_info.pack_configure(pady=(0, 25))
        self.qr_code_entry_frame.pack_configure(fill=X)
        self.qr_code_entry_frame.configure()
        self.right_configurations_frame_1.pack(expand=TRUE)
        self.left_frame.pack_propagate(False)
        self.preview_image.pack_configure(pady=0, padx=0)
        self.preview.pack_propagate(False)
        self.right_frame.pack_propagate(False)

    # Load recent configurations

    def menu_item_selected(self, *args):
        options = self.menu_options
        selected = self.selected_option.get()
        if options and selected:
            match options.index(selected):
                case 0:
                    self.save_qr_code()
                case 1:
                    self.load_json()
                case 2:
                    save_json()
                case 3:
                    open_configurations()
                case 4:
                    open_historic()
                case 5:
                    self.reset_to_defaults()
                case _:
                    messagebox.showinfo('Unknown option', selected)

    def set_historic_path(self, new):
        """
        Sets a new historic path for the app.

        :param new: The new historic path.
        :return:
        """
        self.historic_path = new

    def set_configurations(self):
        """
        Sets configurations for the app.

        :return:
        """
        self.set_historic_path(self.config_file.get('General', 'historic_path') or None)

    @property
    def local_historic(self):
        return self.__local_historic

    @local_historic.setter
    def local_historic(self, historic):
        self.__local_historic = historic

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

    def get_qr_code_logo_size(self):
        return self._qr_code_logo_size.get()

    def set_qr_code_logo_size(self, size):
        self._qr_code_logo_size.set(size)

    @property
    def max_size_preview(self):
        return self._MAX_SIZE_PREVIEW

    @property
    def max_size_historic_thumbnails(self):
        return self._max_size_historic_thumbnails

    @max_size_historic_thumbnails.setter
    def max_size_historic_thumbnails(self, size):
        self.max_size_historic_thumbnails = size

    def reverse_aspect_ratio_flag(self):
        """
		Reverses the QR Code logo aspect ratio Checkbox boolean value.
		"""
        self.logo_image_aspect_ratio_flag = not self.logo_image_aspect_ratio_flag

    def reverse_resize_flag(self):
        """
		Reverses the QR Code logo resize Checkbox boolean value.
		"""
        self.logo_image_resize_flag = not self.logo_image_resize_flag

    def update_preview(self):
        """
		Updates the generated QR Code preview with the GUI values
		"""
        self.grab_set_global()
        img = self.generate_qr_code()
        if self.qr_code_logo_entry.get():
            img = add_qr_code_logo(img, self.qr_code_logo_entry.get())
        if img:
            width, height = img.size
            if (width > self._MAX_SIZE_PREVIEW and height >
                    self._MAX_SIZE_PREVIEW):
                img = img.resize((self._MAX_SIZE_PREVIEW,
                                  self._MAX_SIZE_PREVIEW), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.preview_image.config(image=img_tk)
            self.preview_image.image = img_tk

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_size = buffer.tell()
            file_size = bytes_size_type(file_size)
            self.preview_info.config(
                text=f'Image total size: {width}x{height} px | '
                     f'File size(in memory): {file_size}')
        else:
            self.preview_image.config(image='')
            self.preview_info.config(text="")
        self.grab_release()

    def update_entries(self, entry, task, value="", upd_preview=False,
                       disable=False):
        """
		Apply a specified task to the specified tkinter object or str.
		If task equals "update" updates the entry with the value.
		If task equals "delete" deletes the tkinter object entry value.
		If upd_preview equals True then updates the QR Code self.preview.
		If disable equals True, disables the entry(tkinter object).

		:param entry: tkinter.Entry or str value.
		:param task: The task for the entry.
		:param value: The value to update the entry.
		:param upd_preview: To choose if update the QR code self.preview.
		:param disable: Choose to disable the entry(tkinter object).
		"""
        if entry:
            entry_type = type(entry)
            config = None
            for key, t in self.data_commands.items():
                if t[0]:
                    if t[0]() == entry:
                        config = key
            if (entry_type != str and entry_type not in [Spinbox, StringVar]
                    and confirm_preset(str(value), config)):
                original_state = str(entry.configure()["state"][-1])
                if task == "update":
                    value = str(value)
                    entry.config(state=NORMAL)
                    entry.delete(0, END)
                    match type(entry):
                        case tkinter.Entry:
                            entry.insert(0, value if value is not None else
                            value)
                        case ttk.Combobox:
                            entry.set(value if value is not None else value)
                        case _:
                            pass
                    entry.config(state=original_state)
                elif task == "delete":
                    entry.config(state=NORMAL)
                    entry.delete(0, END)
                    entry.config(state=original_state)
                if disable and entry_type:
                    entry.config(state=DISABLED)
            elif entry_type in [StringVar]:
                if type(value) in [str, int, float] and value != '':
                    entry.set(value)
                else:
                    for values in self.data_commands.values():
                        if values[0]:
                            if values[0]() == entry:
                                entry.set(values[2])
            else:
                return True
            if upd_preview:
                self.update_preview()

    def choose_logo(self):
        """
		Open a file dialog to choose a valid logo image for the QR Code
		"""
        file_types = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("BMP files", "*.bmp")
        ]
        image = filedialog.askopenfile(defaultextension=".png", filetypes
        =file_types)
        if image:
            self.qr_code_logo_entry.config(state=NORMAL)
            self.qr_code_logo_entry.delete(0, END)
            self.qr_code_logo_entry.insert(0, image.name)
            self.qr_code_logo_entry.config(state=DISABLED)
            self.update_preview()
            return Image.open(image.name)
        else:
            self.qr_code_logo_entry.delete(0, END)
            return ""

    def generate_qr_code(self):
        """
		Generate a QR Code image with the specified values.

		:returns: An image object
		"""
        dados = self.qr_code_entry.get()
        cor = confirm_preset(self.qr_code_color_entry.get(), 'color',
                             True) or '#000000'
        version = confirm_preset(self.qr_code_version_entry.get(), 'version',
                                 True)
        border = confirm_preset(self.border_entry.get(), 'border', True)
        box_size = confirm_preset(self.box_size_entry.get(), 'box_size', True)
        bg_color = (confirm_preset(self.bg_color_entry.get(), 'color', True)
                    or "#ffffff")
        if dados:
            version = version
            border = border
            qr = qrcode.QRCode(
                version=version if version else self.default_version,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size,
                border=border
            )
            qr.add_data(dados)
            qr.make(fit=True)
            img = qr.make_image(fill_color=cor, back_color=bg_color or
                                                           '#ffffff')
            if self.qr_code_logo_entry.get():
                img = add_qr_code_logo(img, self.qr_code_logo_entry.get())
            return img

    def save_qr_code(self):
        """
		Generates a QR Code image with the specified values and opens a
		file dialog to save as a valid image file.

		:exception PermissionError: If the program has no permission to
		open the program historic file.

		:exception FileNotFoundError: If the historic file has not been
		found.
		"""
        file_types = [
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("BMP files", "*.bmp")
        ]
        img = self.generate_qr_code()
        if img:
            file = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=file_types)
            if file:
                if file.endswith('.jpg') or file.endswith('.jpeg'):
                    img = convert_image(img, "RGB")
                else:
                    pass
                img.save(file, quality=100)
                qr_code_save_info = {key: value[1]() for key, value in
                                     self.data_commands.items()}

                if not self.local_historic.get(file):
                    self.local_historic.update({file: qr_code_save_info})
                else:
                    self.local_historic[file] = qr_code_save_info

                try:
                    with open(self.historic_path, 'w+') as historic:
                        historic.seek(0)
                        json.dump(self.local_historic, historic, indent=4)
                except (PermissionError, FileNotFoundError):
                    pass
                messagebox.showinfo("Sucesso", f"QR Code salvo como '{file}'")
        else:
            messagebox.showinfo('No data to generate a QR Code',
                                'Please insert some data to '
                                'generate a QR Code.')

    def load_json(self, file=None):
        """
		Load a json QR Code configurations file or dict if "file".

		:param file: If file then configures the QR Code generator with
		the specified dict values.
		:exception KeyError: If are missing keys in the specified dicts.
		"""
        default_configuration = {key: value[1]() for key, value in
                                 self.data_commands.items()}
        configurations = None
        if not file:
            file_path = filedialog.askopenfilename(defaultextension=".json",
                                                   filetypes=[("JSON files",
                                                               "*.json")])
            if file_path:
                file = open(file_path, 'r')
                configurations = (dict(json.load(file)) or
                                  default_configuration)
        elif file:
            configurations = file or default_configuration
        if configurations:
            for key in default_configuration.keys():
                if not configurations.get(key):
                    configurations[key] = ""
            try:
                for key, value in self.data_commands.items():
                    if value[0] and configurations[key] is not None:
                        self.update_entries(value[0](), "update",
                                            configurations[key])
                self.update_preview()
            except KeyError as e:
                print("Missing key: ", e)

    def reset_to_defaults(self):
        """
        Resets all generator configurations.

        :return:
        """
        response = messagebox.askyesno("Reset all generator configurations",
                                       "Are you sure do you want to "
                                       "reset all generator configurations?")
        self.lift()
        if response:
            for key, original in self.data_commands.items():
                if original[0] and key != "data":
                    try:
                        for widget in self.widgets:
                            if widget == original[0]():
                                self.update_entries(widget,
                                                    'update',
                                                    original[2])
                    except ValueError:
                        pass
            self.update_preview()


class Historic(Toplevel):

    def __init__(self):
        super().__init__()
        self.json_window = None
        self.widgets = []
        self.config_file = main_window.config_file
        main_window.style.configure('Treeview', rowheight=100)
        self.historic_options_menu = Menu(self, tearoff=0)
        self.selected_option = StringVar()
        self.selected_option.trace('w', self.menu_item_selected)
        self.option_1 = 'Update historic'
        self.option_2 = 'Change historic location'
        self.historic_options_menu.add_radiobutton(
            label=self.option_1,
            value=self.option_1,
            variable=self.selected_option,
            indicatoron=False
        )
        self.historic_options_menu.add_radiobutton(
            label=self.option_2,
            value=self.option_2,
            variable=self.selected_option,
            indicatoron=False
        )
        self.qr_codes = {}
        self.qr_codes_images = []
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar_h = ttk.Scrollbar(self, orient=HORIZONTAL)
        self.tree_frame = Frame(self, bg="white")
        self.tree = Treeview(self.tree_frame, selectmode='browse')
        for item in self.__dict__.values():
            if getattr(item, '__module__', None) in [tkinter.__name__, ttk.__name__]:
                self.widgets.append(item)
        configure_widgets(self.widgets,
                          main_window.config_file,
                          main_window.widgets_defaults_configurations)

    def menu_item_selected(self, *args):
        """ handle menu selected event """
        selected = self.selected_option.get()
        if selected == self.option_1:
            self.update_data()
        elif selected == self.option_2:
            new_historic = filedialog.askopenfilename(defaultextension='json',
                                                      filetypes=[(
                                                          "JSON files",
                                                          "*.json")])
            if new_historic:
                main_window.config_file['General']['historic_path'] = new_historic
                main_window.historic_path = new_historic
                self.update_data()

    def configure_widgets(self):
        """
		Configures all the widgets for the historic window and updates the data.
		"""
        self.title("Histórico de QR Codes gerados")
        self.config(width=500, height=400)
        columns = ('path', 'image_size', 'image_dimensions', 'date')
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.scrollbar_h.pack(side=BOTTOM, fill=X)
        self.tree_frame.pack(expand=TRUE, fill=BOTH)
        self.tree.config(columns=columns)
        self.tree.heading('#0', text='', anchor=CENTER)
        self.tree.heading('path', text='Caminho', anchor=CENTER)
        self.tree.heading('image_size', text='File size', anchor=CENTER)
        self.tree.heading('image_dimensions', text='Dimensions', anchor=CENTER)
        self.tree.heading('date', text='Data de salvamento', anchor=CENTER)
        self.tree.column('#0', width=0, stretch=NO)
        self.tree.column('path', width=250, anchor=CENTER)
        self.tree.column('image_size', anchor=CENTER)
        self.tree.column('image_dimensions', anchor=CENTER)
        self.tree.column('date', anchor=CENTER)
        self.configure(menu=self.historic_options_menu)
        self.update_data()

    def update_data(self):
        """
		Updates the data of the historic window.
		"""
        try:
            with (open(main_window.historic_path, 'r') as file):
                file = dict(json.load(file))
                if type(file) == dict and file:
                    file = sorted(file.items())[0:100]
                    file = sorted(file,
                                  key=lambda qr_code: qr_code[1]['date'] if
                                  qr_code[1].get('date') else qr_code[0],
                                  reverse=True)
                    self.qr_codes.clear()
                    # self.qr_codes_images.clear()
                    for item in self.tree.get_children():
                        self.tree.delete(item)
                    # Generates data
                    if file:
                        for qr_code_data in file:
                            if not self.qr_codes.get(qr_code_data[0]):
                                image_dimensions = None
                                file_path = qr_code_data[0] or None
                                self.qr_codes[
                                    qr_code_data[0]] = qr_code_data[1]
                                try:
                                    with Image.open(file_path
                                                    ) as qr_code_image:
                                        '''
                                        max_size = main_window \
                                            .max_size_historic_thumbnails
                                        qr_code_image.thumbnail(
                                            (
                                                max_size,
                                                max_size)
                                        )
                                        miniature = ImageTk.PhotoImage(
                                            qr_code_image)
                                        self.qr_codes_images.append(miniature)
                                        '''
                                        image_dimensions = qr_code_image.size
                                        if qr_code_image:
                                            image_size = (
                                                bytes_size_type(path
                                                .getsize(
                                                    file_path)))
                                except (PermissionError, FileNotFoundError):
                                    pass  # miniature = None
                                self.tree.insert("", 'end', open=True,
                                                 # image=miniature or "",
                                                 values=(
                                                     f'{file_path}',
                                                     f'{image_size}',
                                                     f'{image_dimensions[0]}'
                                                     f'x{image_dimensions[1]
                                                     }'
                                                     f' px',
                                                     f'{qr_code_data[1]
                                                        ['date'][0:19] if
                                                     qr_code_data[1]
                                                     .get('date') else
                                                     ""}'
                                                 ))

                self.tree.images = self.qr_codes_images

                def item_selected(event):
                    item_dict = None

                    def configure():
                        if self.json_window:
                            self.json_window.destroy()
                        self.json_window = Toplevel()
                        self.json_window.title = "JSON file"
                        self.json_window.text = Text(self.json_window, height=20)
                        self.json_window.button = Button(self.json_window, text='Generate QR Code',
                                                         command=generate)
                        self.json_window.text.configure(state=NORMAL)
                        self.json_window.text.delete(1.0, END)
                        self.json_window.text.insert(END, str(json.dumps(self.qr_codes[item_dict['values'][0]],
                                                                         indent=4)))
                        self.json_window.text.config(state=DISABLED)
                        self.json_window.text.pack(fill=BOTH)
                        self.json_window.button.pack(pady=40, expand=TRUE)

                    def generate():
                        main_window.load_json(self
                                              .qr_codes[
                                                  item_dict['values'][0]])
                        main_window.generate_qr_code()

                    for selected_item in self.tree.selection():
                        pass
                        item_dict = self.tree.item(selected_item)
                        configure()

                self.tree.bind('<<TreeviewSelect>>', item_selected)
                self.tree.pack(fill=BOTH)
                self.tree.configure(yscrollcommand=self.scrollbar.set,
                                    xscrollcommand=self.scrollbar_h.set)
                self.scrollbar.config(command=self.tree.yview)
                self.scrollbar_h.config(command=self.tree.xview)
        except FileNotFoundError:
            messagebox.showerror('Cannot open the file',
                                 "The file was not found or doesn't"
                                 " exist")
        except PermissionError:
            messagebox.showerror('Cannot open the file',
                                 "The program has no permission to open"
                                 " the file")


class Configurations(Toplevel):

    def __init__(self):
        super().__init__()
        self.title("Configurações")
        self.geometry('800x500')
        self.widgets = []
        self.options_menu = Menu(self, tearoff=0)
        self.selected_option = StringVar()
        self.selected_option.trace('w', self.menu_item_selected)
        self.menu_options = ('Reset configurations',)
        for option in self.menu_options:
            self.options_menu.add_radiobutton(
                label=option,
                value=option,
                variable=self.selected_option,
                indicatoron=False
            )
        self.configure(menu=self.options_menu)
        self.non_triggerable_widgets_frame = LabelFrame(self,
                                                        text="Non-"
                                                             "triggerable "
                                                             "widgets colors",
                                                        bg='white',
                                                        highlightbackground=
                                                        'grey',
                                                        highlightcolor="grey",
                                                        highlightthickness=1)
        self.bg_color_frame = LabelFrame(self.non_triggerable_widgets_frame,
                                         text="Background color")
        self.bg_color_entry = Entry(self.bg_color_frame)
        self.bg_color_entry.insert(0, main_window.config_file.get('Style', 'bgs1') or
                                   "")
        self.bg_color_button = Button(self.bg_color_frame,
                                      text="Escolher cor",
                                      command=lambda color=self
                                      .bg_color_entry:
                                      (choose_color(color),
                                       self.change_windows()))
        self.text_color_frame = LabelFrame(self.non_triggerable_widgets_frame,
                                           text="Text color")
        self.text_color_entry = Entry(self.text_color_frame)
        self.text_color_entry.insert(0, main_window.config_file.get('Style', 'fgs1') or
                                     "")
        self.text_color_button = Button(self.text_color_frame,
                                        text="Escolher cor",
                                        command=lambda color=self
                                        .text_color_entry:
                                        (choose_color(color),
                                         self.change_windows()))
        self.btns_colors_frame = LabelFrame(self, text="Buttons colors",
                                            highlightbackground='grey',
                                            highlightcolor="grey",
                                            highlightthickness=1)
        self.btns_bg_color_frame = LabelFrame(self.btns_colors_frame,
                                              text="Background color")
        self.btns_bg_color_entry = Entry(self.btns_bg_color_frame)
        self.btns_bg_color_entry.insert(0,
                                        main_window.config_file
                                        .get('Style', 'bgs2') or "")
        self.btns_bg_color_button = Button(self.btns_bg_color_frame,
                                           text="Escolher cor",
                                           command=lambda color=self
                                           .btns_bg_color_entry:
                                           (choose_color(color),
                                            self.change_buttons()))
        self.btns_active_bg_color_frame = LabelFrame(self.btns_colors_frame,
                                                     text="Active buttons "
                                                          "background color")
        self.btns_active_bg_color_entry = Entry(self
                                                .btns_active_bg_color_frame)
        self.btns_active_bg_color_entry.insert(0, main_window.config_file
                                               .get('Style', 'active_bgs2') or "")
        self.btns_active_bg_color_button = Button(self
                                                  .btns_active_bg_color_frame,
                                                  text="Escolher cor",
                                                  command=lambda color=self
                                                  .btns_active_bg_color_entry:
                                                  (choose_color(color),
                                                   self.change_buttons()))
        self.btns_text_color_frame = LabelFrame(self.btns_colors_frame,
                                                text="Buttons text color")
        self.btns_text_color_entry = Entry(self.btns_text_color_frame)
        self.btns_text_color_entry.insert(0, main_window
                                          .config_file.get('Style', 'fgs2') or "")
        self.btns_text_color_button = Button(self.btns_text_color_frame,
                                             text="Escolher cor",
                                             command=lambda color=self
                                             .btns_text_color_entry:
                                             (choose_color(color),
                                              self.change_buttons()))
        self.btns_active_text_color_frame = LabelFrame(self.btns_colors_frame,
                                                       text="Active buttons "
                                                            "text color")
        self.btns_active_text_color_entry = Entry(self
                                                  .btns_active_text_color_frame)
        self.btns_active_text_color_entry.insert(0,
                                                 main_window
                                                 .config_file
                                                 .get('Style', 'active_fgs2') or "")
        self.btns_active_text_color_button = Button(self.btns_active_text_color_frame,
                                                    text="Escolher cor",
                                                    command=lambda color=self
                                                    .btns_active_text_color_entry:
                                                    (choose_color(color),
                                                     self.change_buttons()))
        self.other_configurations_frame = LabelFrame(self,
                                                     text="Other configurations",
                                                     bg='white',
                                                     highlightbackground='grey',
                                                     highlightcolor="grey",
                                                     highlightthickness=1)
        self.theme_frame = LabelFrame(self.other_configurations_frame, text="TTK")
        self.chosen_theme = StringVar(self)
        self.themes = main_window.style.theme_names()
        self.theme_label = Label(self.theme_frame, text="TTK widgets theme")
        self.choose_theme = OptionMenu(self.theme_frame, self.chosen_theme,
                                       *self.themes,
                                       command=self.change_theme)
        for item in self.__dict__.values():
            if getattr(item, '__module__', None) in [tkinter.__name__, ttk.__name__]:
                self.widgets.append(item)
        configure_widgets(self.widgets, main_window.config_file,
                          main_window.widgets_defaults_configurations)

    def configure_widgets(self):
        """
		Configures all the Configurations object widgets.
		"""
        config = dict(main_window.config_file.items('Style'))
        for widget in self.widgets:
            if not isinstance(widget, (Menu, Menubutton, StringVar, Style)):
                if not isinstance(widget, (Frame, Label)):
                    widget.pack(pady=5)
                elif isinstance(widget, Label):
                    widget.grid_configure(padx=(10, 0))
                else:
                    widget.configure(bg=config['bgs1'] or None)
                if isinstance(widget, Entry):
                    widget.pack_configure(fill=X, padx=10)
                    widget.config(state=DISABLED)
                elif isinstance(widget, LabelFrame):
                    widget.pack_configure(padx=10, fill=X)
                    widget.configure(bg=config['bgs1'] or None,
                                     fg=config['fgs1'] or None)
                elif isinstance(widget, (Button, OptionMenu)):
                    widget.configure(bg=config['bgs2'] or None,
                                     fg=config['fgs2'] or None,
                                     activebackground=config['active_bgs2'] or
                                                      None,
                                     activeforeground=config['active_fgs2'] or
                                                      None)
            elif isinstance(widget, Style):
                widget.theme_use(config['ttk_theme'] or None)
        self.chosen_theme.set(config['ttk_theme'])
        self.theme_frame.grid_columnconfigure(1, weight=1)
        self.theme_frame.pack_configure(ipady=5)
        self.non_triggerable_widgets_frame.pack_configure(padx=0, pady=0,
                                                          side=LEFT,
                                                          expand=TRUE,
                                                          fill=BOTH)
        self.btns_colors_frame.pack_configure(padx=0, pady=0,
                                              side=LEFT,
                                              expand=TRUE,
                                              fill=BOTH)
        self.other_configurations_frame.pack_configure(padx=0, pady=0,
                                                       side=LEFT,
                                                       expand=TRUE,
                                                       fill=BOTH)
        self.theme_label.grid(row=0, column=0, sticky=W)
        self.choose_theme.grid(row=0, column=1)
        self.choose_theme.configure(width=10)
        self.non_triggerable_widgets_frame.pack_propagate(False)
        self.btns_colors_frame.pack_propagate(False)
        self.other_configurations_frame.pack_propagate(False)

    def reset_to_default(self):
        """
        Resets Configurations object windows configurations.

        :return:
        """
        response = messagebox.askyesno("Reset all configurations",
                                       "Are you sure do you want to "
                                       "reset all configurations?")
        self.lift()
        if response:
            for widget in self.widgets:
                if isinstance(widget, Entry):
                    widget.config(state=NORMAL)
                    widget.delete(0, END)
                    widget.config(state=DISABLED)
                elif isinstance(widget, StringVar):
                    widget.set("")
            self.change_windows()
            self.change_buttons()
            self.change_theme()

    def menu_item_selected(self, *args):
        options = self.menu_options
        selected = self.selected_option.get()
        if options and selected:
            match options.index(selected):
                case 0:
                    self.reset_to_default()
                case _:
                    messagebox.showinfo('Unknown option', selected)

    def change_theme(self, *args):
        """
		Changes all ttk widgets theme.
		:param args:
		:return:
		"""
        main_window.style.theme_use(self.chosen_theme.get() or 'vista')
        main_window.style.configure('Treeview', rowheight=100)
        main_window.config_file['Style']['ttk_theme'] = self.chosen_theme.get()

    def change_windows(self):
        """
		Changes all non-triggerable windows widgets.
		"""
        default = main_window.widgets_defaults_configurations
        bgs_1 = self.bg_color_entry.get()
        fgs_1 = self.text_color_entry.get()
        widgets = []
        widgets.extend(self.widgets)
        widgets.extend(main_window.widgets)
        widgets.extend(main_window.historic_window.widgets) if (
            main_window.historic_window) else None
        for widget in widgets:
            if getattr(widget, '__module__', None) == 'tkinter':
                if not isinstance(widget, (Frame, Button, Entry, StringVar,
                                           Style)):
                    widget.configure(bg=bgs_1 or
                                        default['labelFrame'][0],
                                     fg=fgs_1 or
                                        default['labelFrame'][1])
                    if isinstance(widget, Checkbutton):
                        widget.configure(selectcolor='white')
                elif isinstance(widget, Frame):
                    widget.configure(bg=bgs_1 or default['labelFrame'][0])
        main_window.config_file['Style']['bgs1'] = bgs_1
        main_window.config_file['Style']['fgs1'] = fgs_1

    def change_buttons(self):
        """
		Changes all windows buttons widgets.
		"""
        default = main_window.widgets_defaults_configurations
        bgs_2 = self.btns_bg_color_entry.get()
        fgs_2 = self.btns_text_color_entry.get()
        active_bgs_2 = self.btns_active_bg_color_entry.get()
        active_fgs_2 = self.btns_active_text_color_entry.get()
        widgets = []
        widgets.extend(self.widgets)
        widgets.extend(main_window.widgets)
        widgets.extend(main_window.historic_window.widgets) if (
            main_window.historic_window) else None
        for widget in widgets:
            if isinstance(widget, Button):
                widget.configure(bg=bgs_2 or default['button'][0],
                                 fg=fgs_2 or default['button'][2],
                                 activebackground=active_bgs_2 or
                                                  default['button'][1],
                                 activeforeground=active_fgs_2 or
                                                  default['button'][3])
            elif isinstance(widget, Style):
                widget.theme_use('vista')
        main_window.config_file['Style']['bgs2'] = bgs_2
        main_window.config_file['Style']['fgs2'] = fgs_2
        main_window.config_file['Style']['active_bgs2'] = active_bgs_2
        main_window.config_file['Style']['active_fgs2'] = active_fgs_2


def on_closing():
    """
    Executes events on app closing.

    :return:
    """
    for key, value in main_window.data_commands.items():
        main_window.config_file['Generator'][key] = value[1]()
    with open(main_window.config_path, 'w', encoding='utf-8') as config_file:
        main_window.config_file.write(config_file)
    main_window.destroy()


def open_configurations():
    """
	Create a Configurations object and loads it.
	"""
    global configurations_window
    if configurations_window:
        configurations_window.destroy()
    configurations_window = Configurations()
    configurations_window.configure_widgets()


def open_historic():
    """
	Create a Historic object and loads it.
	"""
    if main_window.historic_window:
        main_window.historic_window.destroy()
    main_window.historic_window = Historic()
    main_window.historic_window.configure_widgets()


def choose_color(entry, upd_preview=False):
    """
	Display a color chooser interface to update an entry with the color.
	"""
    cor = colorchooser.askcolor()[1]
    if cor and type(entry) == Entry:
        entry.config(state=NORMAL)
        entry.delete(0, END)
        entry.insert(0, cor)
        entry.config(state=DISABLED)
        if upd_preview:
            main_window.update_preview()


def configure_widgets(widgets, config_file, default):
    """
    Configures all app widgets.

    :param widgets: Widgets list.
    :param config_file: Configurations dict.
    :param default: Default configurations dict.
    :return:
    """
    if widgets and config_file and default:
        for widget in widgets:
            if getattr(widget, '__module__', None) in [tkinter.__name__]:
                if isinstance(widget, (LabelFrame, Label)):
                    widget.configure(bg=config_file.get('Style', 'bgs1') or
                                        default['labelFrame'][0],
                                     fg=config_file.get('Style', 'fgs1') or
                                        default['labelFrame'][1])
                elif isinstance(widget, Frame):
                    widget.configure(bg=config_file.get('Style', 'bgs1') or
                                        default['labelFrame'][0])
                elif isinstance(widget, (Menubutton, Button)):
                    widget.configure(bg=config_file.get('Style', 'bgs2') or
                                        default['button'][0],
                                     fg=config_file.get('Style', 'fgs2') or
                                        default['button'][2],
                                     activebackground=config_file
                                     .get('Style', 'active_bgs2') or
                                                      default['button'][1],
                                     activeforeground=config_file
                                     .get('Style', 'active_fgs2') or
                                                      default['button'][3])
                elif isinstance(widget, Checkbutton):
                    widget.configure(bg=config_file.get('Style', 'bgs1') or
                                        default['labelFrame'][0],
                                     fg=config_file.get('Style', 'fgs1') or
                                        default['labelFrame'][1],
                                     activebackground=config_file
                                     .get('Style', 'bgs1') or default['labelFrame'][0],
                                     activeforeground=config_file
                                     .get('Style', 'fgs1') or default['labelFrame'][1],
                                     selectcolor=config_file
                                     .get('Style', 'bgs1') or default['labelFrame'][0])
            elif getattr(widget, '__module__', None) in [ttk.__name__]:
                if isinstance(widget, Style):
                    widget.theme_use(config_file.get('Style', 'ttk_theme') or None)
                elif isinstance(widget, (Menubutton, Menu)):
                    widget.configure(bg=config_file.get('Style', 'bgs2') or
                                        default['button'][0],
                                     fg=config_file
                                     .get('Style', 'fgs2') or default['button'][2],
                                     activebackground=config_file
                                     .get('Style', 'active_bgs2') or
                                                      default['button'][1],
                                     activeforeground=config_file
                                     .get('Style', 'active_fgs2') or
                                                      default['button'][3])


def confirm_preset(value, config, return_value=False):
    """
	Returns a flag if the specified value is valid for yours function
	in the config.ini.
	If the return_value is True, returns the value if valid and if the
	flag is True otherwise returns a specified default value for the
	config.ini.

	:param value: The value to check.
	:param config: The value confirmation configuration.
	:param return_value: Returns the value if it and the flag is True
	:returns: A flag if the value is valid for yours configuration and
	return_value is False.
	:returns: value if the flag and return_value are True.
	"""
    if value or type(value) == str and config:
        if main_window.data_commands.get(config):
            default_value = main_window.data_commands[config][2]
            flag = False if value is None else True

            def check_number_config(number):
                if config == 'version':
                    return 40 >= number >= 1
                elif config == 'boxSize':
                    return 10 >= number >= 1
                elif config == 'border':
                    return 4 >= number >= 0
                elif config == 'logoSize':
                    return 4 >= number >= 1

            if value is not None and value.isnumeric():
                flag = check_number_config(int(value))
            elif config == 'color':
                try:
                    ImageColor.getrgb(value)
                    flag = True
                except ValueError:
                    value = ''
                    flag = True
            if not return_value:
                return flag
            else:
                return str(value) if flag or type(value) == str else \
                    default_value


def convert_image(image, convert_to):
    """
	Returns an image converted to the specified type.

	:param image: The image object for conversion.
	:param convert_to: The type of conversion.
	:returns: The converted image object.
	"""
    if image:
        image_type = image.mode
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


def bytes_size_type(size):
    """
    Converts a bytes size value to different units.

    :param size: Bytes value.
    :return: Formatted string with the new value and the measure unit.
    """
    types = ('bytes', 'kb', 'mb', 'gb', 'tb', '>1tb').__iter__()
    selected = next(types)
    while size / 1024 >= 1 and selected != ">1tb":
        size = size / 1024
        selected = next(types)
    return f'{round(size)} {selected}'


def save_json():
    """
	Open a file dialog to save the QR Code configuration as a json file.
	"""
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes
    =[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(
                {key: value[1]() for key, value in main_window.data_commands
                .items()},
                file,
                indent=4
            )


def add_qr_code_logo(img, logo):
    """
	Places an image file in the QR Code image object and returns it.

	:param img: The image object to place the logo.
	:param logo: The image file to place on the img.
	:returns: An image object with the two images merged together.
	:except FileNotFoundError: If the logo file was not found.
	:except PermissionError: If the user has no permission to open the
	logo file.
	"""
    try:
        if img and logo:
            img = img.convert("RGBA")
            logo = Image.open(logo).convert("RGBA")
            if main_window.rar_flag.get() in ['1', '']:
                logo_width, logo_height = img.size
            else:
                logo_width, logo_height = logo.size
            qr_code_width, qr_code_height = img.size
            if main_window.rr_flag.get() in ['1', '']:
                logo_size = main_window.get_qr_code_logo_size() or 0.4
                logo = logo.resize((round(logo_width * float(logo_size)),
                                    round(logo_height * float(logo_size))),
                                   Image.LANCZOS)
            logo_width, logo_height = logo.size
            position = ((qr_code_width - logo_width) // 2, (qr_code_height -
                                                            logo_height
                                                            ) // 2)
            img.paste(logo, position, logo)
            return img
    except FileNotFoundError:
        messagebox.showerror('Cannot open the file',
                             "The file was not found or doesn't exist")
    except PermissionError:
        messagebox.showerror('Cannot open the file',
                             "The program has no permission to open the fil"
                             "e")


if __name__ == "__main__":
    main_window = App()
    main_window.load_json(dict(main_window.config_file.items('Generator')))
    main_window.title("Gerador de QR Code")
    main_window.geometry("800x500")
    main_window.protocol("WM_DELETE_WINDOW", on_closing)
    configurations_window = None
    main_window.mainloop()
