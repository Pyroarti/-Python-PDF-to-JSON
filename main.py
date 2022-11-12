from os import scandir
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import time
import pdfplumber
import re

source_dir = r'C:\Users\rober\Desktop\Python\LMT\LMT_PDF'
dest_dir = r'C:\Users\rober\Desktop\Python\LMT\LMT_DEST'

document_extensions = [".pdf"]

komponent = re.compile(r" {4}\d{2}")
Leverans_datum = re.compile(r"\w{9} \w{3}")
komponent2 = re.compile(r"(?<=ST).*")

result_datum = []
result_komponent = []


class PdfMaker(FileSystemEventHandler):

    def on_created(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.extract_text(name)

    def extract_text(self, name):
        if name.endswith("pdf"):
            with pdfplumber.open(f'{source_dir}\\{name}') as pdf:
                for page in pdf.pages:
                    texts = page.extract_text()
                    self.regex_komponent(texts)
                    self.regex_datum(texts)

    def regex_komponent(self, texts):
        for line1 in texts.split('\n'):
            if komponent.match(line1):
                position1 = ""
                position1 += str(line1 + '\n')
                self.komponentlist(position1)

    def regex_datum(self, texts):
        global result_datum
        for line2 in texts.split('\n'):
            if Leverans_datum.match(line2):
                result_datum.append(line2)

    def komponentlist(self, position1):
        global result_komponent
        komponentslist = position1.splitlines()
        for i, iteminlist in enumerate(komponentslist):
            komponentslist[i] = re.sub((r'(?<=ST).*'), "", komponentslist[i])
            komponentslist[i] = re.sub((r'^\s+|\s+$'), "", komponentslist[i])
            result_komponent.append(komponentslist)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = PdfMaker()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
