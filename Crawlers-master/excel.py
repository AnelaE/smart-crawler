import requests
import pandas as pd

class ExcelProcessor:
    @staticmethod
    def process_excel(url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                excel_content = response.content
                df = pd.read_excel(excel_content)
                # Perform further processing if needed
                return df  # Return the Excel data as a pandas DataFrame
            else:
                print("Failed to fetch Excel file from URL:", url)
                return None
        except Exception as e:
            print("Error processing Excel file:", e)
            return None
