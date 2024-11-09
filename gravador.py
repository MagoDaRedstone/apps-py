import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

class ScreenRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gravador de Tela com FFmpeg")

        self.is_recording = False
        self.process = None

        # Seleção de Plataforma
        self.platform_label = tk.Label(master, text="Selecione a Plataforma:")
        self.platform_label.pack(pady=5)

        self.platform_var = tk.StringVar(value="Linux")  # Valor padrão
        self.platform_options = ["Linux", "Windows", "macOS"]
        self.platform_menu = tk.OptionMenu(master, self.platform_var, *self.platform_options)
        self.platform_menu.pack(pady=5)

        # Entrada de Arquivo de Saída
        self.output_file_label = tk.Label(master, text="Arquivo de Saída:")
        self.output_file_label.pack()
        self.output_file_entry = tk.Entry(master)
        self.output_file_entry.insert(0, "screen_output.mp4")  # valor padrão
        self.output_file_entry.pack(pady=5)

        # Botões
        self.start_button = tk.Button(master, text="Iniciar Gravação", command=self.start_recording)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Parar Gravação", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

    def start_recording(self):
        if not self.is_recording:
            output_file = self.output_file_entry.get()
            platform = self.platform_var.get()

            # Ajusta o comando de acordo com a plataforma
            if platform == "Linux":
                command = f"ffmpeg -f x11grab -i :0.0 -c:v libx264 -pix_fmt yuv420p -r 30 {output_file}"
            elif platform == "Windows":
                command = f"ffmpeg -f gdigrab -i desktop -c:v libx264 -pix_fmt yuv420p -r 30 {output_file}"
            elif platform == "macOS":
                command = f"ffmpeg -f avfoundation -i \"1:\" -c:v libx264 -pix_fmt yuv420p -r 30 {output_file}"

            try:
                # Executa o comando
                self.process = subprocess.Popen(command.split(), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                self.is_recording = True
                self.status_label.config(text="Gravação da tela em andamento...")
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)

                # Cria um thread para monitorar o processo
                threading.Thread(target=self.check_process, daemon=True).start()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao iniciar a gravação: {e}")
                self.is_recording = False
                self.status_label.config(text="Falha ao iniciar gravação.")
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)

    def stop_recording(self):
        if self.is_recording:
            try:
                self.process.terminate()  # Termina o processo do FFmpeg
                self.process.wait()  # Aguarda o processo finalizar
                self.is_recording = False
                self.status_label.config(text="Gravação parada.")
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao parar a gravação: {e}")

    def check_process(self):
        # Monitora a execução do processo
        self.process.wait()
        if self.is_recording:
            self.stop_recording()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorderApp(root)
    root.mainloop()
