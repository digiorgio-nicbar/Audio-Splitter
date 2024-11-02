import os
import subprocess
from pydub import AudioSegment, silence
from PyQt5 import QtWidgets
import sys

class AudioSplitterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Audio Splitter - Suporte a Áudio e Vídeo")

        # Interface gráfica
        self.layout = QtWidgets.QVBoxLayout(self)  # Passe 'self' diretamente aqui para associar o layout ao widget

        self.file_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.file_input)
        self.select_button = QtWidgets.QPushButton('Selecionar Arquivo', self)
        self.layout.addWidget(self.select_button)
        self.select_button.clicked.connect(self.open_file_dialog)

        self.duration_label = QtWidgets.QLabel("Duração dos Segmentos (segundos):")
        self.layout.addWidget(self.duration_label)
        self.duration_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.duration_input)

        self.silence_thresh_label = QtWidgets.QLabel("Limiar de Silêncio (dB):")
        self.layout.addWidget(self.silence_thresh_label)
        self.silence_thresh_input = QtWidgets.QLineEdit(self)
        self.silence_thresh_input.setText("-40")  # Valor padrão
        self.layout.addWidget(self.silence_thresh_input)

        self.start_button = QtWidgets.QPushButton('Iniciar Divisão', self)
        self.layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.split_audio)

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Áudio ou Vídeo", "", "Todos os Arquivos (*);;Arquivos de Áudio (*.mp3 *.wav);;Arquivos de Vídeo (*.mp4 *.mkv)", options=options)
        if file_name:
            self.file_input.setText(file_name)

    def extract_audio(self, video_path, output_audio_path):
        command = [
            'ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', output_audio_path
        ]
        subprocess.run(command)

    def split_audio(self):
        file_path = self.file_input.text()
        if not os.path.isfile(file_path):
            QtWidgets.QMessageBox.warning(self, "Erro", "Arquivo não encontrado!")
            return

        # Verificar se é um vídeo e extrair o áudio se necessário
        if file_path.endswith(('.mp4', '.mkv', '.avi')):
            audio_path = "temp_audio.mp3"
            self.extract_audio(file_path, audio_path)
            file_path = audio_path

        try:
            audio = AudioSegment.from_file(file_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao carregar o arquivo de áudio: {str(e)}")
            return

        # Pegar a duração dos segmentos e limiar de silêncio da interface
        try:
            segment_duration = int(self.duration_input.text()) * 1000  # Convertendo para milissegundos
            silence_thresh = int(self.silence_thresh_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Erro", "Por favor, insira valores válidos para duração e limiar de silêncio.")
            return

        # Dividir o áudio com base nos silêncios detectados
        chunks = silence.split_on_silence(audio, min_silence_len=3000, silence_thresh=silence_thresh)
        if not chunks:
            QtWidgets.QMessageBox.critical(self, "Erro", "Nenhum segmento foi criado. Ajuste os parâmetros e tente novamente.")
            return

        output_dir = os.path.join(os.path.dirname(file_path), "segments")
        os.makedirs(output_dir, exist_ok=True)

        for i, chunk in enumerate(chunks):
            output_file = os.path.join(output_dir, f"segment_{i}.mp3")
            chunk.export(output_file, format="mp3")

        QtWidgets.QMessageBox.information(self, "Sucesso", f"Divisão concluída! Segmentos salvos em: {output_dir}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    splitter_app = AudioSplitterApp()
    splitter_app.show()
    sys.exit(app.exec_())
