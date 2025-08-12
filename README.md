# DentisteDB - PyQt Dental Cabinet Management System

A professional, native PyQt5 desktop application for dental practice management with comprehensive patient care, visit tracking, and interactive dental charting capabilities.

## 🏥 Features

### Core Functionality
- **Patient Management**: Add, edit, view, and delete patient records
- **Visit Tracking**: Record treatments, procedures, and appointments
- **Financial Management**: Track payments, unpaid balances, and revenue
- **X-ray Management**: Upload, view, and manage patient radiographs
- **Search & Filter**: Advanced search and filtering capabilities
- **User Authentication**: Secure login system
- **Data Backup**: Automatic and manual database backup functionality

### Technical Highlights
- **Pure PyQt5**: Native desktop UI with no web dependencies
- **Modular Architecture**: Clean separation of UI, business logic, and data layers
- **SQLite Database**: Local data storage with SQLAlchemy ORM
- **Local File Management**: Secure storage of X-ray images and backups
- **Professional UI**: Modern, responsive interface with proper styling

## 📁 Project Structure

```
pyqt_dental_app/
├── __init__.py
├── main.py                 # Main application entry point
├── db_init.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── models/
│   ├── __init__.py
│   └── database.py        # SQLAlchemy models and database manager
├── services/
│   ├── __init__.py
│   ├── auth_service.py    # Authentication business logic
│   ├── patient_service.py # Patient management logic
│   └── visit_service.py   # Visit management logic
└── ui/
    ├── __init__.py
    ├── login_widget.py     # Login interface
    ├── main_window.py      # Main application window
    ├── patient_list_widget.py      # Patient list view
    ├── patient_form_widget.py      # Patient add/edit form
    ├── patient_detail_widget.py    # Patient details and visits
    ├── visit_form_widget.py        # Visit add/edit form
    └── unpaid_balances_widget.py   # Unpaid balances view
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### 1. Install Dependencies
```bash
cd "path/to/DentisteDB_w7&10 - working"
pip install -r pyqt_dental_app/requirements.txt
```

### 2. Initialize Database
```bash
# Initialize database with default admin user
python pyqt_dental_app/db_init.py --init

# Optional: Add sample data for testing
python pyqt_dental_app/db_init.py --sample-data

# View database information
python pyqt_dental_app/db_init.py --info
```

### 3. Run the Application
```bash
python run_dental_app.py
```

## 🗂️ Data Storage

The application stores data in the user's home directory:
- **Database**: `~/.dentistedb/patients.db`
- **X-ray Images**: `~/.dentistedb/xrays/`
- **Backups**: `~/.dentistedb/backups/`

## 🔧 Database Management

### Initialize Database
```bash
python pyqt_dental_app/db_init.py --init
```

### Reset Database (Delete All Data)
```bash
python pyqt_dental_app/db_init.py --init --reset
```

### Create Backup
```bash
python pyqt_dental_app/db_init.py --backup
```

### Add Sample Data
```bash
python pyqt_dental_app/db_init.py --sample-data
```

### View Database Statistics
```bash
python pyqt_dental_app/db_init.py --info
```

## 📦 Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "DentisteDB" run_dental_app.py
```

The executable will be created in the `dist/` directory.

## 📊 Tableaux de Bord

Le système de tableaux de bord de DentisteDB offre une vue complète et interactive des performances de votre cabinet dentaire. Il comprend trois dashboards principaux accessibles via un système d'onglets moderne.

### 1. 📊 Vue d'ensemble (Dashboard Principal)
**Fichier :** `dashboard_widget.py`

**Fonctionnalités :**
- **Métriques clés** : Total patients, nouveaux patients, RDV du jour, revenus/dépenses mensuels
- **Graphiques** : 
  - Revenus des 6 derniers mois (graphique en barres)
  - Répartition des dépenses par catégorie (graphique circulaire)
- **Tables** :
  - Prochains rendez-vous (5 prochains)
  - Alertes de stock bas
- **Auto-actualisation** : Toutes les 5 minutes

### 2. 💰 Dashboard Financier
**Fichier :** `financial_dashboard_widget.py`

**Fonctionnalités :**
- **KPIs financiers** :
  - Revenus du mois avec pourcentage de croissance
  - Dépenses du mois avec évolution
  - Bénéfice net et marge bénéficiaire
- **Graphiques** :
  - Comparaison revenus vs dépenses (6 mois)
  - Évolution du bénéfice (tendance)
- **Tables** :
  - Factures impayées (top 5)
  - Top dépenses par catégorie

### 3. 👥 Dashboard Patients
**Fichier :** `patient_dashboard_widget.py`

**Fonctionnalités :**
- **Métriques patients** :
  - Total patients
  - Nouveaux patients du mois
  - Patients actifs
  - Taux de fidélisation
- **Graphiques** :
  - Tendance d'inscription des nouveaux patients
  - Répartition par tranche d'âge
- **Tables** :
  - Patients récents (5 derniers)
  - Traitements les plus populaires

## 🏗️ Architecture des Tableaux de Bord

### Structure des Fichiers
```
ui/
├── main_dashboard_widget.py      # Container principal avec onglets
├── dashboard_widget.py           # Dashboard vue d'ensemble
├── financial_dashboard_widget.py # Dashboard financier
└── patient_dashboard_widget.py   # Dashboard patients

services/
└── dashboard_service.py          # Service de données pour dashboards
```

### Composants Principaux

#### `MainDashboardWidget`
- Gestion des onglets de navigation entre les différents tableaux de bord
- Actualisation automatique des données
- Gestion des thèmes et préférences d'affichage
- Export des données et rapports

#### `DashboardService`
- Agrégation des données depuis la base de données
- Calcul des indicateurs clés de performance (KPIs)
- Gestion du cache des données pour des performances optimales
- Interface unifiée pour l'accès aux données

### Design Patterns
- **MVC Pattern**: Séparation claire entre Modèles, Vues et Contrôleurs
- **Service Layer**: Logique métier encapsulée dans des classes de service
- **Repository Pattern**: Accès aux données via la couche service
- **Observer Pattern**: Connexions signal-slot pour la communication UI
- **Singleton Pattern**: Pour le service de données partagé

### Key Components

#### Models (`models/database.py`)
- **User**: Authentication and user management
- **Patient**: Patient information and relationships
- **Visit**: Treatment records and financial tracking
- **DatabaseManager**: Database connection and session management

#### Services (`services/`)
- **AuthService**: User authentication and session management
- **PatientService**: Patient CRUD operations and X-ray management
- **VisitService**: Visit management and financial calculations

#### UI Components (`ui/`)
- **LoginWidget**: User authentication interface
- **MainWindow**: Application shell with navigation
- **PatientListWidget**: Patient browsing and search
- **PatientFormWidget**: Patient data entry and editing
- **PatientDetailWidget**: Comprehensive patient view
- **VisitFormWidget**: Visit recording and editing
- **UnpaidBalancesWidget**: Financial tracking and reporting

## 🔄 Migration from Flask

This PyQt application provides full feature parity with the original Flask application:

| Flask Feature | PyQt Equivalent | Status |
|---------------|-----------------|---------|
| login.html | LoginWidget | ✅ Complete |
| index.html | PatientListWidget | ✅ Complete |
| add_patient.html | PatientFormWidget | ✅ Complete |
| edit_patient.html | PatientFormWidget | ✅ Complete |
| patient_detail.html | PatientDetailWidget | ✅ Complete |
| add_visit.html | VisitFormWidget | ✅ Complete |
| edit_visit.html | VisitFormWidget | ✅ Complete |
| unpaid_balances.html | UnpaidBalancesWidget | ✅ Complete |
| tooth_diagram.html | Placeholder | 🔄 Future |

## 🎨 UI Features

### Modern Interface
- Clean, professional design
- Responsive layouts
- Intuitive navigation
- Keyboard shortcuts
- Context menus
- Drag-and-drop support

### User Experience
- Real-time search and filtering
- Form validation
- Progress indicators
- Status messages
- Confirmation dialogs
- Error handling

## 🔒 Security

- Password hashing with Werkzeug
- Local data storage (no cloud dependencies)
- User session management
- Input validation and sanitization
- Secure file handling

## 🧪 Testing

The modular architecture enables easy unit testing:

```bash
# Future: Run unit tests
python -m pytest tests/
```

## 📈 Future Enhancements

- Tooth diagram functionality
- Report generation (PDF)
- Data import/export
- Multi-user support
- Appointment scheduling
- Backup automation
- Print functionality

## 🐛 Troubleshooting

### Common Issues

1. **PyQt5 Installation Issues**
   ```bash
   pip install --upgrade pip
   pip install PyQt5==5.15.9
   ```

2. **Database Permission Issues**
   - Ensure write permissions to `~/.dentistedb/` directory
   - Run application as administrator if needed

3. **Missing Dependencies**
   ```bash
   pip install -r pyqt_dental_app/requirements.txt
   ```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the database logs
3. Verify file permissions
4. Ensure all dependencies are installed

## 📄 License

This project is for dental practice management use.

---

**DentisteDB v1.0** - Professional Dental Practice Management System
