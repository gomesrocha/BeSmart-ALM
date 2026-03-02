"""Document processing utilities for extracting text from various formats."""
import io
from typing import Optional
from pathlib import Path


class DocumentProcessor:
    """Process and extract text from various document formats."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install pypdf2")
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            import docx
            
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except ImportError:
            raise ImportError("python-docx is required for DOCX processing. Install with: pip install python-docx")
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file."""
        try:
            # Try UTF-8 first
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                return file_content.decode('latin-1').strip()
            except Exception as e:
                raise ValueError(f"Failed to decode text file: {str(e)}")
    
    @staticmethod
    def process_document(filename: str, file_content: bytes) -> str:
        """Process document and extract text based on file extension."""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_content)
        elif file_ext in ['.docx', '.doc']:
            return DocumentProcessor.extract_text_from_docx(file_content)
        elif file_ext == '.txt':
            return DocumentProcessor.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: PDF, DOCX, TXT")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks for better context."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
