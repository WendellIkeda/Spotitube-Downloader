from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QMessageBox
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from downloader import DownloadThread
from youtube_downloader import YoutubeDownloadThread

import sys
import json
import os


CONFIG_FILE = "config.json"


# ==================================================
# CONFIG
# ==================================================

def carregar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except:
        return {"ultima_pasta": ""}


def salvar_config(dados):
    with open(CONFIG_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


config = carregar_config()


# ==================================================
# STATUS
# ==================================================

def atualizar_status(mensagem):
    caixa_status.append(mensagem)


# ==================================================
# PASTA
# ==================================================

def escolher_pasta():

    pasta = QFileDialog.getExistingDirectory(
        janela,
        "Selecione a pasta de destino"
    )

    if pasta:

        campo_pasta.setText(pasta)

        config["ultima_pasta"] = pasta

        salvar_config(config)

        atualizar_status(
            f"✅ Pasta selecionada: {pasta}"
        )


def abrir_pasta():

    pasta = campo_pasta.text().strip()

    if not pasta:

        atualizar_status(
            "⚠ Nenhuma pasta selecionada."
        )

        return

    if not os.path.exists(pasta):

        atualizar_status(
            "❌ A pasta não existe."
        )

        return

    atualizar_status(
        f"📂 Abrindo pasta: {pasta}"
    )

    os.startfile(pasta)


# ==================================================
# DOWNLOAD
# ==================================================

thread_download = None


def download_finalizado():

    botao_download.setEnabled(True)


def iniciar_download():

    url = campo_link.text().strip()

    pasta = campo_pasta.text().strip()

    if not url:

        QMessageBox.warning(
            janela,
            "Aviso",
            "Informe um link."
        )

        return

    if not pasta:

        QMessageBox.warning(
            janela,
            "Aviso",
            "Escolha uma pasta de destino."
        )

        return

    atualizar_status("")
    atualizar_status("🚀 Preparando download...")

    botao_download.setEnabled(False)

    global thread_download

    url_lower = url.lower()

    if (
        "youtube.com" in url_lower
        or
        "youtu.be" in url_lower
    ):

        thread_download = YoutubeDownloadThread(
            url,
            pasta
        )

    elif "spotify.com" in url_lower:

       thread_download = DownloadThread(
           url,
           pasta
       )

    else:

        QMessageBox.warning(
            janela,
            "Aviso",
            "Link não suportado."
        )

        botao_download.setEnabled(True)

        return

    thread_download.log.connect(
        atualizar_status
    )

    thread_download.download_finished.connect(
        download_finalizado
    )

    thread_download.start()


# ==================================================
# APP
# ==================================================

app = QApplication(sys.argv)

janela = QWidget()

janela.setWindowTitle(
    "Spotitube Downloader"
)

janela.resize(
    950,
    750
)

layout = QVBoxLayout()

layout.setAlignment(
    Qt.AlignTop | Qt.AlignHCenter
)

layout.setSpacing(18)

# ==================================================
# TÍTULO
# ==================================================

titulo = QLabel(
    "Spotitube 🎶🎵 Downloader"
)

titulo.setAlignment(
    Qt.AlignCenter
)

fonte_titulo = QFont()

fonte_titulo.setPointSize(26)

fonte_titulo.setBold(True)

titulo.setFont(
    fonte_titulo
)

# ==================================================
# LABELS
# ==================================================

fonte_label = QFont()

fonte_label.setPointSize(11)

# ==================================================
# LINK
# ==================================================

link_label = QLabel(
    "Cole o link do Spotify ou YouTube"
)

link_label.setAlignment(
    Qt.AlignCenter
)

link_label.setFont(
    fonte_label
)

campo_link = QLineEdit()

campo_link.setPlaceholderText(
    "https://open.spotify.com/..."
)

campo_link.setMinimumWidth(
    800
)

campo_link.setMinimumHeight(
    40
)

# ==================================================
# PASTA
# ==================================================

pasta_label = QLabel(
    "Pasta de destino"
)

pasta_label.setAlignment(
    Qt.AlignCenter
)

pasta_label.setFont(
    fonte_label
)

campo_pasta = QLineEdit()

campo_pasta.setText(
    config.get(
        "ultima_pasta",
        ""
    )
)

campo_pasta.setMinimumWidth(
    800
)

campo_pasta.setMinimumHeight(
    40
)

# ==================================================
# BOTÕES PASTA
# ==================================================

layout_botoes = QHBoxLayout()

botao_escolher = QPushButton(
    "Escolher Pasta"
)

botao_abrir = QPushButton(
    "Abrir Pasta"
)

botao_escolher.setMinimumWidth(
    200
)

botao_abrir.setMinimumWidth(
    200
)

botao_escolher.setMinimumHeight(
    40
)

botao_abrir.setMinimumHeight(
    40
)

botao_escolher.clicked.connect(
    escolher_pasta
)

botao_abrir.clicked.connect(
    abrir_pasta
)

layout_botoes.addWidget(
    botao_escolher
)

layout_botoes.addWidget(
    botao_abrir
)

# ==================================================
# DOWNLOAD
# ==================================================

botao_download = QPushButton(
    "BAIXAR"
)

botao_download.setMinimumWidth(
    300
)

botao_download.setMinimumHeight(
    50
)

botao_download.clicked.connect(
    iniciar_download
)

# ==================================================
# STATUS
# ==================================================

status_label = QLabel(
    "Status"
)

status_label.setAlignment(
    Qt.AlignCenter
)

status_label.setFont(
    fonte_label
)

caixa_status = QTextEdit()

caixa_status.setReadOnly(True)

caixa_status.setMinimumWidth(
    850
)

caixa_status.setMinimumHeight(
    220
)

caixa_status.append(
    "🚀 Spotify Downloader iniciado."
)

caixa_status.append(
    "✅ Aguardando comandos..."
)

# ==================================================
# LAYOUT
# ==================================================

layout.addSpacing(20)

layout.addWidget(titulo)

layout.addSpacing(10)

layout.addWidget(link_label)

layout.addWidget(
    campo_link,
    alignment=Qt.AlignCenter
)

layout.addWidget(pasta_label)

layout.addWidget(
    campo_pasta,
    alignment=Qt.AlignCenter
)

layout.addLayout(
    layout_botoes
)

layout.addWidget(
    botao_download,
    alignment=Qt.AlignCenter
)

layout.addSpacing(20)

layout.addWidget(
    status_label
)

layout.addWidget(
    caixa_status,
    alignment=Qt.AlignCenter
)

janela.setLayout(layout)

janela.show()

sys.exit(app.exec())