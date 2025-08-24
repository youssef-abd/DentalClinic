import os
import sys
import random
from datetime import datetime, timedelta, date

# Ensure we run from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Use offscreen Qt platform for headless testing
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt5.QtWidgets import QApplication

from pyqt_dental_app.models.database import DatabaseManager, Patient
from pyqt_dental_app.services.dashboard_service_real import RealDashboardService
from pyqt_dental_app.ui.patient_dashboard_widget import PatientDashboardWidget


def seed_test_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    dbm = DatabaseManager(db_path=db_path)
    dbm.create_tables()
    session = dbm.get_session()
    try:
        # Create patients over the last 8 months to test grouping and averages
        today = date.today()
        created = []

        # Helper to compute date of birth given age
        def dob_for_age(age_years: int):
            try:
                return date(today.year - age_years, max(1, today.month - 1), min(28, today.day))
            except Exception:
                return date(today.year - age_years, 1, 15)

        # Insert patients across months
        month_counts = [3, 5, 2, 6, 4, 7, 1, 3]  # from 8 months ago to now
        for i, count in enumerate(month_counts[::-1]):  # from now backwards
            # compute month i months ago
            base = today
            y, m = base.year, base.month
            for _ in range(i):
                if m == 1:
                    y -= 1
                    m = 12
                else:
                    m -= 1
            created_at = date(y, m, 1)
            for j in range(count):
                p = Patient(
                    nom=f"Nom{i}_{j}",
                    prenom=f"Prenom{i}_{j}",
                    date_naissance=dob_for_age(random.choice([10, 25, 40, 58, 72])),
                    telephone=f"06{random.randint(10000000, 99999999)}",
                    created_at=created_at
                )
                session.add(p)
                created.append(p)

        # Ensure some recent within last 7 days
        for k in range(4):
            p = Patient(
                nom=f"Recent{k}",
                prenom=f"Test{k}",
                date_naissance=dob_for_age(random.choice([20, 33, 47, 66])),
                telephone=f"07{random.randint(10000000, 99999999)}",
                created_at=(today - timedelta(days=random.randint(0, 6)))
            )
            session.add(p)
            created.append(p)

        session.commit()
        return dbm, session
    except Exception:
        session.rollback()
        raise


def main():
    test_db = os.path.join(BASE_DIR, 'test_patients.db')
    dbm, session = seed_test_db(test_db)

    # Headless Qt application
    app = QApplication([])

    # Real service reusing our session
    service = RealDashboardService(session=session)

    # Instantiate the dashboard widget
    widget = PatientDashboardWidget(dashboard_service=service)

    # Extract KPI values
    kpis = []
    if hasattr(widget, 'metric_cards'):
        for card in widget.metric_cards[:5]:
            kpis.append(card.value_label.text())

    # Extract registration trend using the widget's helper
    months, counts = widget._month_labels_and_counts(months=6)

    print('KPI Values (Total, Ce Mois, Par Mois, Par An, Récents):')
    print(', '.join(kpis))
    print('Registration Trend (months -> counts):')
    print(list(zip(months, counts)))

    # Cleanup
    try:
        session.close()
    except Exception:
        pass
    try:
        # remove test db to leave workspace clean
        os.remove(test_db)
    except Exception:
        pass

    # Exit without starting event loop
    sys.exit(0)


if __name__ == '__main__':
    main()
