import base64
import os
import PyPDF2
import docx2txt
from docx import Document


path = "../CV/"
path_txt = "../CV/txt/"


def dispath_base64_type(base64string, name_file):

    if not base64string:
        return ""

    bytes = base64.b64decode(base64string, validate=True)
    complete_path_file = ""
    if bytes[0:4] == b'%PDF':
        complete_path_file = path + name_file + ".pdf"
        convert_b64_2_file(bytes, complete_path_file)
    elif bytes.startswith(b'\x50\x4B'):# verifica se la stringa decodificata inizia con "PK", che indica un file Microsoft Word
        complete_path_file = path + name_file + ".docx"
        convert_b64_2_file(bytes, complete_path_file)
    elif bytes.startswith(b'\xD0\xCF\x11\xE0'):# verifica se la stringa decodificata inizia con "D0CF11E0", che indica un file Microsoft Word doc
        complete_path_file = path + name_file + ".doc"
        convert_b64_2_file(bytes, complete_path_file)
    elif bytes.startswith(b'\xff\xd8'):# verifica se la stringa decodificata inizia con 0xFFD8, che indica un'immagine jpeg
        complete_path_file = path + name_file + ".jpg"
        convert_b64_2_file(bytes, complete_path_file)

    return complete_path_file


def convert_b64_2_file(bytes, name_file):
    try:
        with open(name_file, "wb") as f:
            f.write(bytes)
            f.close()
    except Exception as e:
        print("eccezione" + str(e))


def check_file_type_and_convert(file, name):
    try:
        if not file:
            return ""
        fileobj = open(file, 'rb')
        namefile, extension = os.path.splitext(file)
        if extension == ".pdf":
            return convert_pdf_to_txt(fileobj, name)
        elif extension == ".doc":
            return convert_doc_to_txt(fileobj, name)
        elif extension == ".docx":
            return convert_docx_to_txt(fileobj, name)
        return ""
    except Exception as e:
        print("eccezione" + str(e))


def convert_pdf_to_txt(pdffileobj, name):

    # create reader variable that will read the pdffileobj
    pdfreader = PyPDF2.PdfReader(pdffileobj)
    parts = []
    # This will store the number of pages of this pdf file
    x = len(pdfreader.pages)
    for n in range(0, x):
        print(n)
        page = pdfreader.pages[n]
        parts.append(page.extract_text(visitor_text=visitor_body))
    text_body = "".join(parts)

    file1 = open(path_txt+name+".txt", "w", encoding="utf-8")
    file1.writelines(text_body)
    return text_body


def convert_docx_to_txt(fileobj, name):
    outfile = open(name + '.txt', 'w', encoding='utf-8')
    doc = docx2txt.process(fileobj)
    outfile.write(doc)
    outfile.close()
    fileobj.close()
    return doc


def convert_doc_to_txt(fileobj, name):
    outfile = open(name + '.txt', 'w', encoding='utf-8')
    document = Document(fileobj)
    paragrafi = []
    # leggiamo tutti i paragrafi
    for paragrafo in document.paragraphs:
        print(paragrafo.text)
        paragrafi.append(paragrafo.text)
    text = " ".join(paragrafi)
    outfile.write(text)
    outfile.close()
    return text


def visitor_body(text, cm, tm, fontDict, fontSize):
    parts = []
    y = tm[5]
    if y > 50 and y < 720:
        parts.append(text)
    return parts

#a = check_file_type_and_convert("../CV/Aljosa Marinkovic.docx", "Aljosa Marinkovic").encode('utf-8')
#b = check_file_type_and_convert("../CV/Andra Hazaparu.docx", "Andra Hazaparu").encode('utf-8')
#c = check_file_type_and_convert("../CV/Aoife Marie Fitzgerald.docx", "Aoife Marie Fitzgerald").encode('utf-8')



