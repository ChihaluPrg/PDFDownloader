import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
import os

# 対象のURL
url = 'https://sukiruma.net/kanji-work24m_2nen/'

# ページを取得
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# ダウンロード先のフォルダを作成
os.makedirs('pdfs', exist_ok=True)

# PDFファイルのURLを取得
pdf_urls = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').endswith('.pdf')]

# PDFファイルをダウンロード
pdf_paths = []
for pdf_url in pdf_urls:
    pdf_name = os.path.join('pdfs', pdf_url.split('/')[-1])
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

output_path = 'merged.pdf'
merger.write(output_path)
merger.close()

print(f'Merged PDF saved as: {output_path}')
