import subprocess
import threading
import os
import platform
import urllib.request
import zipfile
import tarfile
import time
import signal
import sys

class ScreenRecorderApp:
    def __init__(self):
        self.is_recording = False
        self.process = None
        self.ffmpeg_path = None
        self.resolution = "1920x1080"  # Resolução padrão
        self.fps = 30  # FPS padrão
        self.bitrate = "2000k"  # Bitrate padrão
        self.quality = "medium"  # Qualidade padrão (média)

    def setup(self):
        """Verifica e instala o FFmpeg, se necessário"""
        self.ffmpeg_path = self.check_ffmpeg()  # Verifica se o FFmpeg está no diretório ou subpastas
        if not self.ffmpeg_path:
            print("FFmpeg não encontrado. Baixando e instalando...")
            self.download_ffmpeg()

    def check_ffmpeg(self):
        """Verifica se o FFmpeg está disponível na pasta ou subpastas"""
        ffmpeg_bin_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
        ffmpeg_path = self.find_ffmpeg(ffmpeg_bin_dir)
        return ffmpeg_path

    def find_ffmpeg(self, directory):
        """Procura pelo ffmpeg nas subpastas"""
        for root, dirs, files in os.walk(directory):
            if "ffmpeg" in files:
                return os.path.join(root, "ffmpeg")
        return None

    def download_ffmpeg(self):
        """Baixa e instala o FFmpeg no sistema"""
        ffmpeg_bin_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
        os_type = platform.system()

        if not os.path.exists(ffmpeg_bin_dir):
            os.makedirs(ffmpeg_bin_dir)

        if os_type == "Windows":
            url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = os.path.join(ffmpeg_bin_dir, "ffmpeg.zip")
            print("Baixando FFmpeg...")
            try:
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(ffmpeg_bin_dir)
                os.remove(zip_path)
            except Exception as e:
                print(f"Erro ao baixar ou extrair o FFmpeg para Windows: {e}")
                return None

        elif os_type == "Linux" or os_type == "Darwin":  # macOS também usa 'Darwin'
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"
            tar_path = os.path.join(ffmpeg_bin_dir, "ffmpeg.tar.xz")
            print("Baixando FFmpeg...")
            try:
                urllib.request.urlretrieve(url, tar_path)
                with tarfile.open(tar_path, 'r:xz') as tar_ref:
                    tar_ref.extractall(ffmpeg_bin_dir)
                os.remove(tar_path)
            except Exception as e:
                print(f"Erro ao baixar ou extrair o FFmpeg para Linux/macOS: {e}")
                return None

        else:
            print("Erro: Sistema operacional não suportado.")
            return None

    def start_recording(self, output_file):
        if not self.ffmpeg_path:
            print("Erro: FFmpeg não encontrado.")
            return

        if not self.is_recording:
            os_type = platform.system()

            # Ajusta o comando de acordo com a plataforma
            if os_type == "Linux":
                command = [self.ffmpeg_path, "-f", "x11grab", "-i", ":0.0", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(self.fps), "-b:v", self.bitrate, output_file]
            elif os_type == "Windows":
                command = [self.ffmpeg_path, "-f", "gdigrab", "-i", "desktop", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(self.fps), "-b:v", self.bitrate, output_file]
            elif os_type == "Darwin":  # macOS
                command = [self.ffmpeg_path, "-f", "avfoundation", "-i", "1:", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(self.fps), "-b:v", self.bitrate, output_file]

            try:
                # Executa o comando
                self.process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                self.is_recording = True
                print("Gravação da tela em andamento...")

                # Cria um thread para monitorar o processo
                threading.Thread(target=self.check_process, daemon=True).start()
                # Inicia o contador do timer
                threading.Thread(target=self.show_timer, daemon=True).start()

            except Exception as e:
                print(f"Erro ao iniciar a gravação: {e}")
                self.is_recording = False

    def stop_recording(self):
        if self.is_recording:
            try:
                self.process.terminate()  # Termina o processo do FFmpeg
                self.process.wait()  # Aguarda o processo finalizar
                self.is_recording = False
                print("\nGravação parada.")
            except Exception as e:
                print(f"Erro ao parar a gravação: {e}")

    def show_timer(self):
        start_time = time.time()
        try:
            while self.is_recording:
                elapsed_time = int(time.time() - start_time)
                minutes = elapsed_time // 60
                seconds = elapsed_time % 60
                # Limpar o terminal e mostrar o tempo de gravação
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                print(f"Gravando... Tempo de gravação: {minutes:02}:{seconds:02}")
                print("\nDigite 'stop' para parar a gravação ou pressione Ctrl + C.")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nGravação interrompida com Ctrl+C.")
            self.stop_recording()

    def check_process(self):
        # Monitora a execução do processo
        self.process.wait()
        if self.is_recording:
            self.stop_recording()

    def show_main_menu(self):
        sys.stdout.write("\033[H\033[J")  # Limpa o terminal
        print(f"Gravador de Tela:")
        """Exibe o menu principal"""
        while True:
            print("\n1 - Iniciar gravação")
            print("2 - Configurações")
            print("3 - Verificar / Instalar FFmpeg")
            print("4 - Sair")
            choice = input("Escolha uma opção: ").strip()

            if choice == "1":
                output_file = input("Digite o nome do arquivo de saída (ex: screen_output.mp4): ").strip()
                self.start_recording(output_file)
            elif choice == "2":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                self.show_config_menu()
            elif choice == "3":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                self.show_check_install_menu()
            elif choice == "4":
                print("Saindo...")
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                break
            else:
                print("Opção inválida.")

    def show_check_install_menu(self):
        sys.stdout.write("\033[H\033[J")  # Limpa o terminal
        """Exibe o menu de verificação e instalação do FFmpeg"""
        while True:
            print("\n1 - Verificar FFmpeg")
            print("2 - Instalar FFmpeg")
            print("3 - Voltar ao menu principal")
            choice = input("Escolha uma opção: ").strip()

            if choice == "1":
                if self.ffmpeg_path:
                    sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                    print(f"FFmpeg encontrado em: {self.ffmpeg_path}")
                else:
                    sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                    print("FFmpeg não encontrado.")
            elif choice == "2":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                print("Iniciando instalação do FFmpeg...")
                self.setup()  # Baixa e configura o FFmpeg
            elif choice == "3":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                break
            else:
                print("Opção inválida.")

    def show_config_menu(self):
        sys.stdout.write("\033[H\033[J")  # Limpa o terminal
        """Exibe o menu de configurações"""
        while True:
            print("\n1 - Resolução")
            print("2 - FPS")
            print("3 - Bitrate")
            print("4 - Qualidade")
            print("5 - Voltar ao menu principal")
            choice = input("Escolha uma opção: ").strip()

            if choice == "1":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                self.change_resolution()
            elif choice == "2":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                self.change_fps()
            elif choice == "3":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                self.change_bitrate()
            elif choice == "4":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                self.change_quality()
            elif choice == "5":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                break
            else:
                print("Opção inválida.")

    def change_resolution(self):
        """Muda a resolução da gravação"""
        resolution = input("Digite a resolução (ex: 1920x1080): ").strip()
        self.resolution = resolution
        print(f"Resolução alterada para {self.resolution}")

    def change_fps(self):
        """Muda o FPS da gravação"""
        fps = input("Digite o FPS (ex: 30): ").strip()
        self.fps = int(fps)
        print(f"FPS alterado para {self.fps}")

    def change_bitrate(self):
        """Muda o bitrate da gravação"""
        bitrate = input("Digite o bitrate (ex: 2000k): ").strip()
        self.bitrate = bitrate
        print(f"Bitrate alterado para {self.bitrate}")

    def change_quality(self):
        sys.stdout.write("\033[H\033[J")  # Limpa o terminal
        """Muda a qualidade da gravação"""
        while True:
            print("\n1 - Baixa")
            print("2 - Média")
            print("3 - Alta")
            print("4 - Voltar")
            choice = input("Escolha uma opção de qualidade: ").strip()

            if choice == "1":
                self.quality = "low"
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                print("Qualidade alterada para baixa.")
                break
            elif choice == "2":
                self.quality = "medium"
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                print("Qualidade alterada para média.")
                break
            elif choice == "3":
                self.quality = "high"
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                print("Qualidade alterada para alta.")
                break
            elif choice == "4":
                sys.stdout.write("\033[H\033[J")  # Limpa o terminal
                break
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    app = ScreenRecorderApp()
    app.show_main_menu()
