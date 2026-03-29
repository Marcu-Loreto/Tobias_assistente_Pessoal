"""
core/document_parser.py
Funções de extração de texto para diferentes formatos de arquivo.
Suporta: .pdf, .docx, .xlsx, .csv, .txt
"""
import io
import pandas as pd
import fitz  # PyMuPDF
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extrai texto de um arquivo PDF usando PyMuPDF."""
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extrai parágrafos de um arquivo Word (.docx)."""
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])


def extract_text_from_excel(file_bytes: bytes) -> str:
    """Converte todas as abas de um arquivo Excel para tabelas Markdown."""
    try:
        df_dict = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        text = ""
        for sheet_name, df in df_dict.items():
            text += f"\n--- Aba: {sheet_name} ---\n"
            text += df.to_markdown(index=False) + "\n"
        return text
    except Exception as e:
        return f"Erro ao ler arquivo Excel: {e}"


def extract_text_from_csv(file_bytes: bytes) -> str:
    """Converte um CSV em tabela Markdown legível pelo LLM."""
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df.to_markdown(index=False)
    except Exception as e:
        return f"Erro ao ler arquivo CSV: {e}"


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decodifica arquivo de texto com fallback para latin-1."""
    try:
        return file_bytes.decode("utf-8")
    except Exception:
        return file_bytes.decode("latin-1")


def parse_uploaded_file(uploaded_file) -> str:
    """
    Dispatcher central: recebe um objeto UploadedFile do Streamlit
    e despacha para o parser correto com base na extensão.
    """
    name = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif name.endswith(".xlsx"):
        return extract_text_from_excel(file_bytes)
    elif name.endswith(".csv"):
        return extract_text_from_csv(file_bytes)
    elif name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        return f"Formato não suportado: {uploaded_file.name}"
