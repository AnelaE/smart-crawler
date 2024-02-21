from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk
nltk.download('punkt')
nltk.download('stopwords')

class LanguageProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))  # Assuming English as default language
        self.stemmer = SnowballStemmer('english')  # Assuming English as default language

    def detect_language(self, text):
        try:
            language = detect(text)
            return language
        except LangDetectException:
            print("Error: Unable to detect language.")
            return None

    def process_text(self, text, language=None):
        if not language:
            language = self.detect_language(text)
        if language:
            tokens = word_tokenize(text)
            filtered_tokens = [word for word in tokens if word.lower() not in self.stop_words]
            stemmed_words = [self.stemmer.stem(word) for word in filtered_tokens]
            processed_text = ' '.join(stemmed_words)
            return processed_text
        return None
