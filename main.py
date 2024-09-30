import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QMessageBox, QInputDialog
from datetime import datetime
import json

class StockApp(QWidget):

    def save_data(self):
        data = {
            'articles': self.articles,
            'vendus': self.vendus
        }
        with open('stock_data.json', 'w') as file:
            json.dump(data, file)

    def load_data(self):
        try:
            with open('stock_data.json', 'r') as file:
                data = json.load(file)
                self.articles = data['articles']
                self.vendus = data['vendus']
                self.update_stock_table()
                self.update_sold_table()
        except FileNotFoundError:
            self.articles = []
            self.vendus = []

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion de Stock")
        self.resize(600, 400)
        
        # Initialiser les données
        self.articles = []
        self.vendus = []

        # Créer les éléments de l'interface
        self.layout = QVBoxLayout()

        # Formulaire pour ajouter des articles
        self.formLayout = QFormLayout()
        self.nom_input = QLineEdit()
        self.unite_input = QLineEdit()
        self.prix_input = QLineEdit()
        self.quantite_input = QLineEdit()
        self.formLayout.addRow('Nom:', self.nom_input)
        self.formLayout.addRow('Unité:', self.unite_input)
        self.formLayout.addRow('Prix unitaire:', self.prix_input)
        self.formLayout.addRow('Quantité:', self.quantite_input)

        self.add_button = QPushButton("Ajouter l'article")
        self.add_button.clicked.connect(self.add_article)
        self.formLayout.addWidget(self.add_button)

        self.layout.addLayout(self.formLayout)

        # Tableau des articles en stock
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)  # Ajouter une colonne pour la date d'achat
        self.stock_table.setHorizontalHeaderLabels(["Nom", "Unité", "Prix Unitaire", "Quantité", "Date d'Achat"])
        self.layout.addWidget(QLabel("Articles en Stock:"))
        self.layout.addWidget(self.stock_table)

        # Tableau des articles vendus
        self.sold_table = QTableWidget()
        self.sold_table.setColumnCount(5)  # Ajouter une colonne pour la date de vente
        self.sold_table.setHorizontalHeaderLabels(["Nom", "Prix de Vente", "Quantité", "Date de Vente","Prix d'Achat"])
        self.layout.addWidget(QLabel("Articles Vendus:"))
        self.layout.addWidget(self.sold_table)

        # Ajouter des boutons pour vendre des articles et calculer le bénéfice
        self.sell_button = QPushButton("Vendre un article")
        self.sell_button.clicked.connect(self.sell_article)
        self.layout.addWidget(self.sell_button)

        self.benefit_button = QPushButton("Afficher le bénéfice")
        self.benefit_button.clicked.connect(self.show_benefit)
        self.layout.addWidget(self.benefit_button)

        # Configuration finale
        self.setLayout(self.layout)
        self.load_data()

    def add_article(self):
        nom = self.nom_input.text()
        unite = self.unite_input.text()
        prix = self.prix_input.text()
        quantite = self.quantite_input.text()

        # Générer la date du jour
        date_achat = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not nom or not unite or not prix or not quantite:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return

        # Ajouter l'article à la liste
        self.articles.append([nom, unite, prix, quantite, date_achat])
        self.update_stock_table()

        # Vider les champs après l'ajout
        self.nom_input.clear()
        self.unite_input.clear()
        self.prix_input.clear()
        self.quantite_input.clear()
        self.save_data()

    def update_stock_table(self):
        self.stock_table.setRowCount(len(self.articles))
        for row, article in enumerate(self.articles):
            for col, data in enumerate(article):
                self.stock_table.setItem(row, col, QTableWidgetItem(data))

    def sell_article(self):
        nom, ok = QInputDialog.getText(self, "Vente", "Nom de l'article vendu:") 
        if not ok or not nom:
            return
        
        prix, ok = QInputDialog.getText(self, "Vente", "Prix de vente:") 
        if not ok or not prix:
            return

        quantite, ok = QInputDialog.getText(self, "Vente", "Quantité vendue:") 
        if not ok or not quantite:
            return

        # Générer la date de vente
        date_vente = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Vérifier si l'article existe dans le stock
        for article in self.articles:
            if article[0] == nom and int(article[3]) >= int(quantite):
                # Mettre à jour le stock
                article[3] = str(int(article[3]) - int(quantite))
                if int(article[3]) == 0:
                    self.articles.remove(article)

                # Ajouter à la liste des articles vendus
                self.vendus.append([nom, prix, quantite, date_vente, article[2]])  # article[2] est le prix d'achat
                self.update_stock_table()
                self.update_sold_table()
                self.save_data()
                return
        
        QMessageBox.warning(self, "Erreur", "Article introuvable ou quantité insuffisante")

    def update_sold_table(self):
        self.sold_table.setRowCount(len(self.vendus))
        for row, vendu in enumerate(self.vendus):
            for col, data in enumerate(vendu):
                self.sold_table.setItem(row, col, QTableWidgetItem(data))

    def show_benefit(self):
        total_benefit = 0
        for vendu in self.vendus:
            nom, prix_vente, quantite, _, prix_achat = vendu # Le "_" est utilisé pour ignorer la date de vente
            total_benefit += (float(prix_vente) - float(prix_achat)) * int(quantite)             
        QMessageBox.information(self, "Bénéfice", f"Bénéfice total: {total_benefit}XOF")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockApp()
    window.show()
    sys.exit(app.exec_())
