import requests
import os
from PIL import Image
import pytesseract

class ImageProcessor:
    @staticmethod
    def process_image(url, folder_path):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_content = response.content

                # Extract filename from URL
                filename = url.split('/')[-1]

                # Save image content to a file
                image_path = os.path.join(folder_path, filename)
                image_dir = os.path.dirname(image_path)
                os.makedirs(image_dir, exist_ok=True)  # Ensure the directory exists

                with open(image_path, 'wb') as file:
                    file.write(image_content)

                # Perform OCR on the image
                extracted_text = ImageProcessor.perform_ocr(image_path)

                # Save extracted text to a file
                text_filename = filename.split('.')[0] + '.txt'
                text_path = os.path.join(folder_path, text_filename)
                with open(text_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(extracted_text)

                # Save image path to a file
                image_list_path = os.path.join(folder_path, 'image_list.txt')
                with open(image_list_path, 'a', encoding='utf-8') as image_list_file:
                    image_list_file.write(f"{filename}: {text_filename}\n")

                return image_path  # Return the path to the saved image file
            else:
                return None
        except Exception as e:
            return None

    @staticmethod
    def perform_ocr(image_path):
        try:
            # Perform OCR using pytesseract
            pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
            extracted_text = pytesseract.image_to_string(Image.open(image_path))
            return extracted_text.strip() if extracted_text else ''
        except Exception as e:
            return None