import requests
from PyPDF2 import PdfMerger
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QGridLayout
from PyQt5.QtCore import QSettings
import re
import io

class PDFDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # ウィンドウの設定
        self.setWindowTitle('PDF Downloader & Merger')

        # QSettingsオブジェクトを作成
        self.settings = QSettings('MyCompany', 'PDFDownloader')

        # ウィンドウ位置とサイズを復元
        self.restore_window_settings()

        # 保存ファイル名ラベルと入力ボックス
        self.filename_label = QLabel('保存するファイル名:')
        self.filename_entry = QLineEdit()

        # 保存先を設定するボタン
        self.browse_button = QPushButton('保存先を設定')
        self.browse_button.clicked.connect(self.set_default_save_location)

        # ボタン
        self.download_button = QPushButton('ダウンロードして統合')
        self.download_button.clicked.connect(self.download_and_merge_pdfs)

        # URL入力フィールドの初期化
        self.url_entries = []

        # グリッドレイアウトの初期化 (縦10×横4)
        self.url_inputs_layout = QGridLayout()

        # 40個のURLフィールドを配置
        self.add_initial_url_fields()

        # メインレイアウト
        layout = QVBoxLayout()
        layout.addLayout(self.url_inputs_layout)
        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_entry)
        layout.addWidget(self.browse_button)
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

        # 前回の保存先を復元
        self.default_save_path = self.settings.value('default_save_path', '')

    def restore_window_settings(self):
        """保存されたウィンドウの位置とサイズを復元する"""
        default_geometry = self.settings.value("geometry", None)
        if default_geometry:
            self.restoreGeometry(default_geometry)

    def closeEvent(self, event):
        """ウィンドウを閉じる前に位置とサイズを保存する"""
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def set_default_save_location(self):
        """デフォルトの保存先を設定する"""
        folder = QFileDialog.getExistingDirectory(self, '保存先を選択してください')
        if folder:
            self.default_save_path = folder
            self.settings.setValue('default_save_path', folder)
            QMessageBox.information(self, '成功', f'デフォルトの保存先が設定されました: {folder}')

    def sanitize_filename(self, filename):
        """ファイル名をクリーニングして適切な形式にする"""
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        return filename

    def add_initial_url_fields(self):
        """40個のURLフィールドを配置する"""
        for i in range(40):
            url_label = QLabel(f'URL {i + 1}:')
            url_entry = QLineEdit()
            self.url_entries.append(url_entry)

            # URLフィールドをグリッドレイアウトに配置
            row = i % 10  # 縦に10個
            column = i // 10  # 10個を超えると次の列へ

            self.url_inputs_layout.addWidget(url_label, row, column * 2)
            self.url_inputs_layout.addWidget(url_entry, row, column * 2 + 1)

    def download_and_merge_pdfs(self):
        urls = [url_entry.text() for url_entry in self.url_entries if url_entry.text()]
        filename = self.filename_entry.text()

        if not urls:
            QMessageBox.warning(self, 'エラー', '少なくとも1つのURLを入力してください。')
            return

        if not filename:
            QMessageBox.warning(self, 'エラー', '保存するファイル名を入力してください。')
            return

        # デフォルトの保存先が設定されていない場合は警告
        if not self.default_save_path:
            QMessageBox.warning(self, 'エラー', 'デフォルトの保存先が設定されていません。')
            return

        # PDFファイルを一時保存せず、直接メモリ内で結合
        merger = PdfMerger()

        for url in urls:
            try:
                # PDFファイルをダウンロード
                response = requests.get(url, stream=True)
                content_type = response.headers.get('Content-Type')

                # URLが直接PDFでない場合も対応
                if 'pdf' in content_type:
                    # PDFのバイナリデータをメモリ内で処理
                    pdf_data = io.BytesIO(response.content)
                    merger.append(pdf_data)
                else:
                    raise ValueError(f"URL {url} はPDFファイルではありません。")
            except Exception as e:
                QMessageBox.warning(self, 'エラー', f'ダウンロードエラー: {e}')
                return

        # 保存ファイル名を指定して保存
        output_path = os.path.join(self.default_save_path, f'{self.sanitize_filename(filename)}.pdf')
        with open(output_path, 'wb') as f_out:
            merger.write(f_out)

        merger.close()

        QMessageBox.information(self, '成功', f'PDFの統合が完了しました。\nファイル保存場所: {output_path}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFDownloader()
    window.show()
    sys.exit(app.exec_())
