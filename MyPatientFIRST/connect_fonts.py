# Import neccessary modules
from PyQt6.QtGui import QFont, QFontDatabase

# Function to load Google Fonts into the application
def load_google_fonts(font_path):
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print("Failed to load font. Falling back to default.")
        return QFont("Calibri", 10)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    return QFont(font_family, 10)