from tkinter import *
from tkinter import messagebox
from customtkinter import *
import openai
import pyperclip
import time
from tkinter import StringVar
from gtts import gTTS
import playsound   # playsound version 1.2.2
import os
from PIL import Image
from math import floor
import authorization
from threading import Thread

set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
set_widget_scaling(0.8)


class WindowAPIKey(CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.apiKeyVar = StringVar()
        self.api_key_set = ''

        # configure window
        self.title("API Key Settings")
        self.geometry(f"{420}x{200}")
        self.iconbitmap(default='LogoTransparent.ico')

        self.logo_label = CTkLabel(self, text="Input your openai API Key below:", font=CTkFont(size=12, weight="bold"))
        self.logo_label.pack(padx=10, pady=10)
        self.entry = CTkEntry(self, textvariable=self.apiKeyVar, placeholder_text="Please Enter your openai API Key", placeholder_text_color="white", width=400)
        self.entry.pack(padx=10)
        self.status_label = CTkLabel(self, text='')
        self.status_label.pack(padx=10, pady=5)
        self.save_btn = CTkButton(self, text="Save", command=self.btn_apikey_event)
        self.save_btn.pack(padx=10)
        self.close_btn = CTkButton(self, text="Close", command=self.destroy)
        self.close_btn.pack(padx=10, pady=10)

    def setAPIKey(self):
        ev = authorization.EnvivarSettings('OPENAI_API_KEY')
        status = ev.setEnvVar(self.api_key_set)
        if status:
            self.lbl_text(self.status_label, 'API Key successfully saved.\nPlease restart your PC.')
            self.entry.delete(0, 'end')
        else:
            self.lbl_text(self.status_label, 'Save API key unsuccessfully!')

    def btn_apikey_event(self):
        self.api_key_set = self.apiKeyVar.get()
        self.lbl_text(self.status_label, 'Saving API key in process ......')
        self.update()
        tAPI = Thread(target=self.setAPIKey())
        tAPI.start()

    def lbl_text(self, lblwidget, txt):
        tmp_lblwidget = lblwidget
        tmp_lblwidget.configure(text=txt)






class App(CTk):
    def __init__(self):
        super().__init__()

        self.model = "text-davinci-003"
        self.temperature = 0.5
        self.max_tokens = 1024
        self.api_key = ''
        self.request_var = StringVar()
        self.voice_switch_status = StringVar()
        self.language = 'de'
        self.sound = False
        self.api_key_set = ''

        # configure window
        self.title("Desktop AI ChatBot")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")
        self.iconbitmap(default='LogoTransparent.ico')
        #self.attributes('-fullscreen', True)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=13, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = CTkLabel(self.sidebar_frame, text="Desktop AI ChatBot", font=CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=10, pady=(20, 10))

        current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = CTkImage(Image.open(current_path + "/icon.png"), size=(150, 150))
        self.bg_image_label = CTkLabel(self.sidebar_frame, image=self.bg_image, text="")
        self.bg_image_label.grid(row=0, column=1, pady=20)

        self.copy_btn = CTkButton(self.sidebar_frame, text="Copy conversation",
                                  command=lambda: self.clipboard_copy(self.textbox.get("0.0", "end")))
        self.copy_btn.grid(row=1, column=0, padx=10, pady=10)

        self.print_btn = CTkButton(self.sidebar_frame, text="Save conversation", command=self.export)
        self.print_btn.grid(row=1, column=1, padx=10, pady=10)

        self.clear_btn = CTkButton(self.sidebar_frame, text="Clear conversation", command=self.clear)
        self.clear_btn.grid(row=2, column=1, padx=10, pady=10)

        self.exit_btn = CTkButton(self.sidebar_frame, text="Exit", command=self.destroy)
        self.exit_btn.grid(row=2, column=0, padx=10, pady=10)

        self.api_btn = CTkButton(self.sidebar_frame, text="API Key Setting", command=self.btn_apikey_event)
        self.api_btn.grid(row=3, column=0, padx=10, pady=10)

        self.language_mode_label = CTkLabel(self.sidebar_frame, text="Voice Language:", anchor="w")
        self.language_mode_label.grid(row=9, column=0, padx=10, pady=(0, 0))

        self.mode_label = CTkLabel(self.sidebar_frame, text="Voice Language:", anchor="w")
        self.mode_label.grid(row=9, column=0, padx=10, pady=(0, 0))

        self.language_mode_option_menu = CTkOptionMenu(self.sidebar_frame, values=["de", "en", "cs", "pl", "sk"],
                                                       command=self.change_language_mode_event)
        self.language_mode_option_menu.grid(row=10, column=0, padx=10, pady=(0, 0))

        self.mode_option_menu = CTkOptionMenu(self.sidebar_frame, values=["de", "en", "cs", "pl", "sk"],
                                              command=self.change_language_mode_event)
        self.mode_option_menu.grid(row=10, column=0, padx=10, pady=(0, 0))

        self.appearance_mode_label = CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=10, pady=(0, 0))

        self.appearance_mode_option_menu = CTkOptionMenu(self.sidebar_frame, values=["Dark", "System"],
                                                         command=self.change_appearance_mode_event)
        self.appearance_mode_option_menu.grid(row=6, column=0, padx=10, pady=(0, 0))

        self.voice_label = CTkLabel(self.sidebar_frame, text="Voice ON/OFF:", anchor="w")
        self.voice_label.grid(row=13, column=1, padx=10, pady=(0, 0))

        self.scaling_label = CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=5, column=1, padx=10, pady=(0, 0))

        self.scaling_option_menu = CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%"],
                                                 command=self.change_scaling_event)
        self.scaling_option_menu.grid(row=6, column=1, padx=10, pady=(0, 0))

        self.voice_switch = CTkSwitch(self.sidebar_frame, text="Voice", command=self.voice_select,
                                      variable=self.voice_switch_status, onvalue="On", offvalue="Off")
        self.voice_switch.grid(row=14, column=1, padx=10, pady=(20, 20))

        self.api_label = CTkLabel(self.sidebar_frame, text="API Key: missing", anchor="w")
        self.api_label.grid(row=3, column=1, padx=10, pady=(0, 0))

        self.screen_label = CTkLabel(self.sidebar_frame, text="Screen", anchor="w")
        self.screen_label.grid(row=9, column=1, padx=10, pady=(0, 0))

        self.screen_mode = CTkOptionMenu(self.sidebar_frame, values=["Normal", "Full"],
                                                         command=self.change_screen_mode)
        self.screen_mode.grid(row=10, column=1, padx=10, pady=(0, 0))

        self.slider_lenght_label = CTkLabel(self.sidebar_frame, text="Max. tokens: ", anchor="w",
                                            font=CTkFont(size=12, weight="bold"))
        self.slider_lenght_label.grid(row=11, column=0, padx=10, pady=(0, 0))

        self.slider_lenght = CTkSlider(self.sidebar_frame, from_=0, to=4000, number_of_steps=4000,
                                       command=self.lenght_slider)
        self.slider_lenght.grid(row=11, column=1, padx=10, pady=(20, 20), sticky="ew")

        self.slider_temp_label = CTkLabel(self.sidebar_frame, text="Temperature: ", anchor="w",
                                          font=CTkFont(size=12, weight="bold"))
        self.slider_temp_label.grid(row=12, column=0, padx=10, pady=(0, 0))

        self.slider_temp = CTkSlider(self.sidebar_frame, from_=0, to=1000, number_of_steps=1000,
                                     command=self.temp_slider)
        self.slider_temp.grid(row=12, column=1, padx=10, pady=(20, 20), sticky="ew")
        self.slider_temp.configure(command=self.temp_slider)

        self.model_label = CTkLabel(self.sidebar_frame, text="Model:", anchor="w")
        self.model_label.grid(row=13, column=0, padx=10, pady=(0, 0))

        self.model_option_menu = CTkOptionMenu(self.sidebar_frame,
                                               values=["text-davinci-003", "text-curie-001", "text-babbage-001",
                                                       "text-ada-001", "code-davinci-002", "code-cushman-001"],
                                               command=self.change_model_event)
        self.model_option_menu.grid(row=14, column=0, padx=10, pady=(0, 10))



        # create main entry and button
        self.entry = CTkEntry(self, textvariable=self.request_var, placeholder_text="Please Enter your question")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 20), pady=(20, 10), sticky="nsew")

        self.send_btn = CTkButton(master=self, text="Send Question",
                                  command=lambda: self.chatAI(self.model, self.request_var.get(), self.temperature,
                                                              self.max_tokens, self.api_key))
        self.send_btn.grid(row=4, column=1, padx=(20, 20), pady=(0, 20), sticky="nsew")

        # create textbox
        self.textbox = CTkTextbox(self, width=300, font=("Helvetica", 18))
        self.textbox.grid(row=0, rowspan=3, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.init_slider(self.max_tokens, self.slider_lenght, self.slider_lenght_label, 1, 'Max. tokens: ')
        self.init_slider(self.temperature, self.slider_temp, self.slider_temp_label, 1000, 'Temperature: ')

        self.loadAPIKey()

    def scree_update(self, full):
        self.attributes('-fullscreen', full)
        self.update()


    def loadAPIKey(self):
        ev = authorization.EnvivarSettings('OPENAI_API_KEY')
        status, val = ev.getEnvVar()
        if status:
            self.api_key = val
            self.api_label.configure(text='API Key: OK')
        else:
            self.api_label.configure(text='API Key: missing')

    def btn_apikey_event(self):
        self.apiKey_window = WindowAPIKey(self)
        self.apiKey_window.grab_set()

    def change_model_event(self, new_model_mode: str):
        self.model = new_model_mode

    def change_language_mode_event(self, new_language_mode: str):
        self.language = new_language_mode

    def change_appearance_mode_event(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    def change_screen_mode(self, new_screen_mode: str):
        if new_screen_mode == 'Normal':
            self.scree_update(False)
        elif new_screen_mode == 'Full':
            self.scree_update(True)
        else:
            pass

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        set_widget_scaling(new_scaling_float)

    def export(self):
        try:
            t = time.localtime()
            timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)
            text_file = f'conversation{timestamp}.txt'
            text_file_opn = open(text_file, "w", encoding="utf-8")
            text_file_opn.write(self.textbox.get(0.0, 'end'))
            text_file_opn.close()
        except Exception as e:
            self.textbox.insert(0.0,
                                'Sorry there was a problem with saving the text into a text file.\n' + str(e) + '\n')
            self.textbox.insert(0.0, '\nError:\n')

    def clear(self):
        self.textbox.delete(0.0, 'end')

    def clipboard_copy(self, text):
        pyperclip.copy(text)

    def voice_select(self):
        temp_status = self.voice_switch_status.get()
        if temp_status == 'On':
            self.sound = True
        elif temp_status == 'Off':
            self.sound = False
        else:
            pass

    def lenght_slider(self, new_value):
        str_val = f'Max. tokens: {floor(new_value)}'
        self.slider_lenght_label.configure(text=str_val)
        self.max_tokens = floor(new_value)

    def temp_slider(self, new_value):
        str_val = 'Temperature: ' + '{0:.2f}'.format(new_value / 1000)
        self.slider_temp_label.configure(text=str_val)
        self.temperature = new_value / 1000

    def init_slider(self, value, slider_widget, label_widget, calc_faktor, additional_text):
        slider_widget.set(value * calc_faktor)
        label_widget.configure(text=f'{additional_text} {str(value)}')

    @staticmethod
    def response_audio(audio, lang):
        tts = gTTS(text=audio, lang=lang)
        file = 'audio.mp3'
        tts.save(file)
        playsound.playsound(file)
        os.remove(file)

    def chatAI(self, model, request, temperature, max_tokens, api_key):
        try:
            if request != '':
                response = openai.Completion.create(model=model, prompt=request, temperature=temperature,
                                                    max_tokens=max_tokens, api_key=api_key, top_p=0, logprobs=10)
                answer = response.choices[0].text
                self.textbox.insert(0.0, self.request_var.get() + '\n')
                self.textbox.insert(0.0, '\nQuestion:\n')
                self.textbox.insert(0.0, answer + '\n')
                self.textbox.insert(0.0, '\nAnswer:\n')
                if self.sound:
                    self.response_audio(answer, self.language)
                self.entry.delete(0, 'end')
            else:
                self.textbox.insert(0.0, 'Please enter any statement!\n')
                self.textbox.insert(0.0, '\nAnswer:\n')
        except Exception as e:
            self.textbox.insert(0.0,
                                'Sorry there is something wrong, first please check your internet connection or try again later.\n' + str(
                                    e) + '\n')
            self.textbox.insert(0.0, '\nAnswer:\n')


if __name__ == "__main__":
    app = App()
    app.mainloop()