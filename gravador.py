import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import platform
import urllib.request
import zipfile
import tarfile

class ScreenRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gravador de Tela com FFmpeg")

        self.is_recording = False
        self.process = None
        self.ffmpeg_path = self.check_ffmpeg()  # Verifica ou instala o FFmpeg

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

    def check_ffmpeg(self):
        try:
            # Tenta verificar se o ffmpeg já está disponível
            subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "ffmpeg"  # FFmpeg está no PATH
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Baixar e instalar ffmpeg se não estiver disponível
        os_type = platform.system()
        ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg_bin")

        if not os.path.exists(ffmpeg_dir):
            os.makedirs(ffmpeg_dir)

        if os_type == "Windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)
            os.remove(zip_path)
            ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg-release-essentials", "bin", "ffmpeg.exe")

        elif os_type == "Linux" or os_type == "Darwin":  # macOS também usa 'Darwin'
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
            tar_path = os.path.join(ffmpeg_dir, "ffmpeg.tar.xz")
            urllib.request.urlretrieve(url, tar_path)
            with tarfile.open(tar_path, 'r:xz') as tar_ref:
                tar_ref.extractall(ffmpeg_dir)
            os.remove(tar_path)
            ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg")

        else:
            messagebox.showerror("Erro", "Sistema operacional não suportado.")
            return None

        # Retorna o caminho para o executável do ffmpeg
        return ffmpeg_exe if os.path.exists(ffmpeg_exe) else None

    def start_recording(self):
        if not self.ffmpeg_path:
            messagebox.showerror("Erro", "FFmpeg não encontrado e não pôde ser instalado.")
            return

        if not self.is_recording:
            output_file = self.output_file_entry.get()
            platform = self.platform_var.get()

            # Ajusta o comando de acordo com a plataforma
            if platform == "Linux":
                command = [self.ffmpeg_path, "-f", "x11grab", "-i", ":0.0", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", output_file]
            elif platform == "Windows":
                command = [self.ffmpeg_path, "-f", "gdigrab", "-i", "desktop", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", output_file]
            elif platform == "macOS":
                command = [self.ffmpeg_path, "-f", "avfoundation", "-i", "1:", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", output_file]

            try:
                # Executa o comando
                self.process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
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
