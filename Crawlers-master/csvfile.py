import requests
import csvfile
from io import StringIO

class CsvProcessor:
    @staticmethod
    def process_csv(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                csv_content = response.text
                # Use StringIO to convert string to file-like object
                csv_file = StringIO(csv_content)
                reader = csvfile.reader(csv_file)
                data = []
                for row in reader:
                    data.append(row)
                # Perform further processing if needed
                return data  # Return the CSV data as a list of lists
            else:
                print("Failed to fetch CSV from URL:", url)
                return None
        except Exception as e:
            print("Error processing CSV:", e)
            return None
