from PySide6.QtCore import QThread, Signal

import subprocess
import sys
import re
import os


class DownloadThread(QThread):

    log = Signal(str)
    download_finished = Signal()

    def __init__(self, url, pasta):
        super().__init__()

        self.url = url
        self.pasta = pasta

        self.sucessos = 0
        self.falhas = 0

    def run(self):

        arquivos_antes = {
            arquivo
            for arquivo in os.listdir(self.pasta)
            if arquivo.lower().endswith(".mp3")
        }

        comando = [
            sys.executable,
            "-m",
            "spotdl",
            "--ffmpeg",
            "C:\\ffmpeg\\ffmpeg.exe",
            self.url,
            "--output",
            self.pasta
        ]

        try:

            self.log.emit("🚀 Iniciando SpotDL...")

            processo = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            for linha in processo.stdout:

                linha = linha.strip()

                if not linha:
                    continue

                if "Found" in linha and "songs in" in linha:
                    self.log.emit(f"📋 {linha}")
                    continue

                if linha.startswith('Downloaded "'):

                    resultado = re.search(
                        r'Downloaded "(.*?)"',
                        linha
                    )

                    if resultado:

                        musica = resultado.group(1)

                        self.sucessos += 1

                        self.log.emit(
                            f"✅ Baixado: {musica}"
                        )

                    continue

                if "AudioProviderError" in linha:

                    self.falhas += 1

                    self.log.emit(
                        "❌ Falha no download de uma música."
                    )

                    continue

                if "LookupError" in linha:

                    self.falhas += 1

                    self.log.emit(
                        "❌ Música não encontrada."
                    )

                    continue

                if "youtube.com" in linha:
                    continue

                if "YouTube Music returned no usable results" in linha:
                    continue

            processo.wait()

            arquivos_depois = {
                arquivo
                for arquivo in os.listdir(self.pasta)
                if arquivo.lower().endswith(".mp3")
            }

            novos_arquivos = sorted(
                arquivos_depois - arquivos_antes
            )

            if novos_arquivos:

                self.log.emit("")
                self.log.emit("🔊 Iniciando normalização...")

                for arquivo in novos_arquivos:

                    caminho_original = os.path.join(
                        self.pasta,
                        arquivo
                    )

                    nome_base = os.path.splitext(
                        caminho_original
                    )[0]

                    caminho_temp = (
                        nome_base
                        + "_normalizado.mp3"
                    )

                    self.log.emit(
                        f"🔊 Normalizando: {arquivo}"
                    )

                    comando_normalizacao = [
                        "C:\\ffmpeg\\ffmpeg.exe",
                        "-y",
                        "-i",
                        caminho_original,
                        "-af",
                        "loudnorm=I=-14:LRA=11:TP=-1.5",
                        caminho_temp
                    ]

                    resultado = subprocess.run(
                        comando_normalizacao,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    if resultado.returncode == 0:

                        try:

                            os.remove(
                                caminho_original
                            )

                            os.rename(
                                caminho_temp,
                                caminho_original
                            )

                        except Exception as erro:

                            self.log.emit(
                                f"⚠ Erro ao substituir arquivo: {erro}"
                            )

                    else:

                        self.log.emit(
                            f"⚠ Falha na normalização: {arquivo}"
                        )

                self.log.emit(
                    "✅ Normalização concluída."
                )

            self.log.emit("")
            self.log.emit("━━━━━━━━━━━━━━━━━━━━")
            self.log.emit(
                f"✅ Sucessos: {self.sucessos}"
            )
            self.log.emit(
                f"❌ Falhas: {self.falhas}"
            )
            self.log.emit("━━━━━━━━━━━━━━━━━━━━")

            if processo.returncode == 0:

                self.log.emit(
                    "🎉 Processo finalizado."
                )

            else:

                self.log.emit(
                    "⚠ Processo finalizado com avisos."
                )

        except Exception as erro:

            self.log.emit(
                f"❌ Erro: {erro}"
            )

        self.download_finished.emit()