import os

import LanguageProcessor as LanguageProcessor
import psycopg2
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from excel import ExcelProcessor
from image import ImageProcessor
from pdf import PdfProcessor
from word import WordProcessor
from csvfile import CsvProcessor
from langdetect.lang_detect_exception import LangDetectException
import pika

class WebCrawler:
    def __init__(self):
        self.visited_links = set()

        # Set up RabbitMQ connection parameters
        self.connection_parameters = pika.ConnectionParameters('localhost')
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='DemoQueue', durable=True)
        self.channel.basic_consume(queue='DemoQueue', on_message_callback=self.on_message_received, auto_ack=True)

        # Connect to the PostgreSQL database
        self.conn = psycopg2.connect(
            host='localhost',
            database='Smart-crawler',
            user='postgres',
            password='***',
            port='5432'
        )
        self.cursor = self.conn.cursor()

        # Create table if not exists
        self.create_table()

    def start_consuming(self):
        print('Waiting for messages...')
        self.channel.start_consuming()

    def on_message_received(self, ch, method, properties, body):
        url = body.decode('utf-8')
        print(f"Received URL: {url}")
        self.crawl(url, depth=5)

    def crawl(self, url, depth=5):
        if depth == 0:
            return
        if url not in self.visited_links:
            self.visited_links.add(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    self.extract_content(url, soup)

                    # Extract href links
                    href_links = [link.get('href') for link in soup.find_all('a', href=True)]
                    for link in href_links:
                        absolute_link = urljoin(url, link)
                        self.crawl(absolute_link, depth - 1)

                    # Extract img links
                    img_links = [image.get('src') for image in soup.find_all('img', src=True)]
                    for img_link in img_links:
                        absolute_img_link = urljoin(url, img_link)
                        self.crawl(absolute_img_link, depth - 1)

            except Exception as e:
                pass  # Silently ignore crawling errors

    def extract_content(self, url, soup):
        # Extract content based on content type
        if url.lower().endswith(('.html', '.htm')):
            # Extract text content
            text_content = soup.get_text()
            self.save_content(url, text_content, 'txt')
            self.save_content_to_database(url, text_content, 'txt')
        elif url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Process image
            image_processor = ImageProcessor()
            folder_path = 'images'  # Set the folder path where you want to save the images
            processed_image_path = image_processor.process_image(url, folder_path)
            if processed_image_path:
                # Save image path to a file
                self.save_content(url, processed_image_path, 'txt')
                self.save_content_to_database(url, processed_image_path, 'txt')
        elif url.lower().endswith('.docx'):
            # Process Word document
            word_processor = WordProcessor()
            processed_text = word_processor.process_word(url)
            if processed_text:
                self.save_content(url, processed_text, 'txt')
                self.save_content_to_database(url, processed_text, 'txt')
        elif url.lower().endswith('.csv'):
            # Process CSV
            csv_processor = CsvProcessor()
            processed_data = csv_processor.process_csv(url)
            if processed_data:
                self.save_content(url, str(processed_data), 'txt')
                self.save_content_to_database(url, str(processed_data), 'txt')
        elif url.lower().endswith('.pdf'):
            # Process PDF
            pdf_processor = PdfProcessor()
            num_pages = pdf_processor.process_pdf(url)
            if num_pages:
                self.save_content(url, str(num_pages), 'txt')
                self.save_content_to_database(url, str(num_pages), 'txt')
        elif url.lower().endswith(('.xls', '.xlsx')):
            # Process Excel
            excel_processor = ExcelProcessor()
            processed_data = excel_processor.process_excel(url)
            if processed_data:
                self.save_content(url, str(processed_data), 'txt')
                self.save_content_to_database(url, str(processed_data), 'txt')

    def process_text(self, url, text):
        try:
            language_processor = LanguageProcessor()
            language = language_processor.detect_language(text)
            print(f"Detected language: {language}")
            # Check if language is supported
            if language in ['en', 'fr', 'es']:  # Add more supported languages as needed
                processed_text = language_processor.process_text(text, language)
                if processed_text:
                    self.save_content(url, processed_text, 'txt')
                    self.save_content_to_database(url, text, 'txt')
                else:
                    print("Error processing text.")
            else:
                print(f"Language '{language}' not supported for processing.")
        except LangDetectException as e:
            print(f"Error detecting language for {url}: {e}")

    def save_content(self, url, content, content_type):
        # Save content to a file
        folder_path = self.get_folder_path(content_type)
        file_name = f"{url.split('/')[-1]}.{content_type}"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    def save_content_to_database(self, url, content, content_type):
        try:
            # Insert the content into the database
            sql = "INSERT INTO your_table (url, content, content_type) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (url, content, content_type))
            self.conn.commit()
            print("Content saved to database successfully!")
        except Exception as e:
            print(f"Error saving content to database: {e}")

    def get_folder_path(self, content_type):
        if content_type.lower() in ('pdf', 'docx', 'xlsx', 'xls', 'csv', 'txt'):
            folder_name = content_type
        elif content_type.lower() in ('jpg', 'jpeg', 'png', 'gif'):
            folder_name = 'images'
        else:
            # For other content types, create a folder named 'other'
            folder_name = 'other'

        folder_path = os.path.join('.', folder_name)
        os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists
        return folder_path

    def create_table(self):
        try:
            # SQL query to create table
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS your_table (
                    id SERIAL PRIMARY KEY,
                    url TEXT,
                    content TEXT,
                    content_type TEXT
                )
            '''
            # Execute the SQL query
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print("Table created successfully!")
        except Exception as e:
            print(f"Error creating table: {e}")

    def __del__(self):
        # Close the database connection when the object is deleted
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    crawler = WebCrawler()
    crawler.start_consuming()
