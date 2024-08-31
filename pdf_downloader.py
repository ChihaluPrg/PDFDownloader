import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings


class PDFDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # ウィンドウの設定
        self.setWindowTitle('PDF Downloader & Merger')

        # QSettingsオブジェクトを作成
        self.settings = QSettings('MyCompany', 'PDFDownloader')

        # ウィンドウ位置とサイズを復元
        self.restore_window_settings()

        # URLラベルと入力ボックス
        self.url_label = QLabel('対象のURL:')
        self.url_entry = QLineEdit()

        # 保存ファイル名ラベルと入力ボックス
        self.filename_label = QLabel('保存するファイル名:')
        self.filename_entry = QLineEdit()

        # ボタン
        self.download_button = QPushButton('ダウンロードして統合')
        self.download_button.clicked.connect(self.download_and_merge_pdfs)

        # レイアウト
        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_entry)
        layout.addWidget(self.download_button)
        self.setLayout(layout)

        # スタイルシート (QSS)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def restore_window_settings(self):
        """保存されたウィンドウの位置とサイズを復元する"""
        # デフォルトの位置とサイズ（初回起動時などのため）
        default_geometry = self.settings.value("geometry", None)

        if default_geometry:
            self.restoreGeometry(default_geometry)

    def closeEvent(self, event):
        """ウィンドウを閉じる前に位置とサイズを保存する"""
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def download_and_merge_pdfs(self):
        url = self.url_entry.text()
        filename = self.filename_entry.text()

        if not url:
            QMessageBox.warning(self, 'エラー', 'URLを入力してください。')
            return

        if not filename:
            QMessageBox.warning(self, 'エラー', '保存するファイル名を入力してください。')
            return

        # ページを取得
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ダウンロード先のフォルダを選択
        folder = QFileDialog.getExistingDirectory(self, '保存先フォルダを選択してください')
        if not folder:
            QMessageBox.warning(self, 'エラー', '保存先のフォルダが選択されていません。')
            return

        os.makedirs(os.path.join(folder, 'pdfs'), exist_ok=True)

        # PDFファイルのURLを取得
        pdf_urls = [link.get('href') for link in soup.find_all('a') if
                    link.get('href') and link.get('href').endswith('.pdf')]

        if not pdf_urls:
            QMessageBox.warning(self, 'エラー', '指定されたURLにはPDFファイルが見つかりませんでした。')
            return

        pdf_paths = []
        for pdf_url in pdf_urls:
            pdf_name = os.path.join(folder, 'pdfs', pdf_url.split('/')[-1])
            pdf_paths.append(pdf_name)

            # PDFファイルをダウンロード
            response = requests.get(pdf_url)
            with open(pdf_name, 'wb') as f:
                f.write(response.content)
                print(f'Downloaded: {pdf_name}')

        # PDFファイルを統合
        merger = PdfMerger()
        for pdf_path in pdf_paths:
            merger.append(pdf_path)

        # 保存ファイル名を指定して保存
        output_path = os.path.join(folder, f'{filename}.pdf')
        merger.write(output_path)
        merger.close()

        QMessageBox.information(self, '成功', f'PDFの統合が完了しました。\nファイル保存場所: {output_path}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFDownloader()
    window.show()
    sys.exit(app.exec_())
