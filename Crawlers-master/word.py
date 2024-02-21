import requests
from docx import Document
from io import BytesIO

class WordProcessor:
    @staticmethod
    def process_word(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                doc_content = response.content
                doc = Document(BytesIO(doc_content))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                # Perform further processing if needed
                return text  # Return the text content of the Word document
            else:
                print("Failed to fetch Word document from URL:", url)
                return None
        except Exception as e:
            print("Error processing Word document:", e)
            return None
