import io
import requests
from PyPDF2 import PdfReader

class PdfProcessor:
    @staticmethod
    def process_pdf(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                pdf_content = response.content
                pdf_reader = PdfReader(io.BytesIO(pdf_content))
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"  # Extract text from each page and append
                # Perform further processing if needed
                return text_content.strip()  # Return the concatenated text content
            else:
                print("Failed to fetch PDF from URL:", url)
                return None
        except Exception as e:
            print("Error processing PDF:", e)
            return None