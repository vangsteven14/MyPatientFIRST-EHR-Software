from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation

# Load Hide/Show Side Widgets Icons ------------------------------------------------------- #
class MainUIWidgetsButtons():
    def __init__(self, ui):
        self.ui = ui
        
    def load_hide_icons(self):
        pixmap = QPixmap("icons/MyPatientFirstLogo_Symbol.JPG")
        self.ui.logo_1.setPixmap(pixmap)
        self.ui.home_btn_1.setIcon(QIcon('icons/home.svg'))
        self.ui.patient_btn_1.setIcon(QIcon('icons/patient.svg'))
        self.ui.visit_btn_1.setIcon(QIcon('icons/visit.svg'))
        self.ui.billings_btn_1.setIcon(QIcon('icons/billings.svg'))
        self.ui.exit_btn_1.setIcon(QIcon('icons/exit.svg'))

    def load_show_icons(self):
        pixmap = QPixmap("icons/MyPatientFirstLogo_Symbol.JPG")
        self.ui.logo_2.setPixmap(pixmap)
        self.ui.home_btn_2.setIcon(QIcon('icons/home.svg'))
        self.ui.patient_btn_2.setIcon(QIcon('icons/patient.svg'))
        self.ui.visit_btn_2.setIcon(QIcon('icons/visit.svg'))
        self.ui.billings_btn_2.setIcon(QIcon('icons/billings.svg'))
        self.ui.exit_btn_2.setIcon(QIcon('icons/exit.svg'))

    # Function for changing menu page via side widget buttons --------------------------------- #
    def connect_buttons(self):
        # Functions for side widgets menu page
        self.ui.menu_btn_1.toggled.connect(self.menu_tab_toggled)       # Still in progress for side widgets delay animation

        self.ui.home_btn_1.toggled.connect(self.home_btn_toggled)
        self.ui.home_btn_2.toggled.connect(self.home_btn_toggled)

        self.ui.patient_btn_1.toggled.connect(self.patient_btn_toggled)
        self.ui.patient_btn_2.toggled.connect(self.patient_btn_toggled)

        self.ui.visit_btn_1.toggled.connect(self.visit_btn_toggled)
        self.ui.visit_btn_2.toggled.connect(self.visit_btn_toggled)

        self.ui.billings_btn_1.toggled.connect(self.billings_btn_toggled)
        self.ui.billings_btn_2.toggled.connect(self.billings_btn_toggled)

        # Functions for page 1 widgets page
        self.ui.home_btn_1.clicked.connect(self.home_btn_toggled)
        self.ui.home_btn_2.clicked.connect(self.home_btn_toggled)
        self.ui.pg1_patients_btn.clicked.connect(self.pg1_patients_btn_toggled)
        self.ui.pg1_visits_btn.clicked.connect(self.pg1_visits_btn_toggled)
        self.ui.pg1_billings_btn.clicked.connect(self.pg1_billings_btn_toggled)

        # Ensures stacked widget pages is changed
        self.ui.stackedWidget.currentChanged.connect(self.stackedWidget_currentChanged)

        # Ensure buttons are checkable
        self.set_buttons_checkable()

    def set_buttons_checkable(self):
        buttons = [
            self.ui.home_btn_1, self.ui.home_btn_2,
            self.ui.patient_btn_1, self.ui.patient_btn_2,
            self.ui.visit_btn_1, self.ui.visit_btn_2,
            self.ui.billings_btn_1, self.ui.billings_btn_2,
            self.ui.pg1_patients_btn,
            self.ui.pg1_visits_btn,
            self.ui.pg1_billings_btn
        ]
        for btn in buttons:
            btn.setCheckable(True)

    # Function for changing page to user page ----------------------------------------------- #
    def user_btn_clicked(self):
        print(f"Switching to page 3. Total pages: {self.ui.stackedWidget.count()}")
        if self.ui.stackedWidget.count() > 3:
            self.ui.stackedWidget.setCurrentIndex(3)
        else:
            print("Error: Page index 3 does not exist!")

    def menu_tab_toggled(self):
        pass

    def stackedWidget_currentChanged(self, index):
        btn_list = self.ui.side_widget_1.findChildren(QPushButton) + self.ui.side_widget_2.findChildren(QPushButton)

        for btn in btn_list:
            if index in [2, 3]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)

        # Get the current widget from the stackedWidget and apply an opacity effect/animation
        # to the current widget
        current_widget = self.ui.stackedWidget.widget(index)
        effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(effect)
        
        # Create an animation to fade in the widget from 0 to 1 opacity
        delayed_animation = QPropertyAnimation(effect, b"opacity")
        delayed_animation.setDuration(250)
        delayed_animation.setStartValue(0)
        delayed_animation.setEndValue(1)
        delayed_animation.start()
        
        # Updates the current animation
        self.current_animation = delayed_animation

    # Functions for buttons changing pages on side widgets menu page ----------------------- #
    def home_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def patient_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def visit_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def billings_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    # Functions for buttons changing pages on page 1 widgets page ----------------------- #
    def pg1_patients_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        
    def pg1_visits_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def pg1_billings_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)