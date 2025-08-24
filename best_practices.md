# 📘 Project Best Practices

## 1. Project Purpose
A desktop application for dental practice management built with PyQt5 and SQLAlchemy. It manages patients, visits, unpaid balances, inventory, invoicing, and provides financial dashboards. Data is stored in a local SQLite database under the user profile. The UI is primarily French-localized. Optional dashboard features provide trends and KPI visualizations using Matplotlib (SciPy optional). Some auxiliary scripts exist for synchronization (e.g., Supabase).

## 2. Project Structure
- Root
  - run_dental_app.py — launcher for the desktop app
  - README.md, INSTALLATION_GUIDE.md, WINDOWS_7_COMPATIBILITY.md — documentation
  - requirements_win7.txt — dependency pin set compatible with older Windows
  - package.json/app.json/eas.json — companion tooling (not used by the PyQt app)
- pyqt_dental_app/
  - main.py — PyQt entry point; initializes DB, services, and windows
  - db_init.py — DB bootstrap (if present)
  - requirements.txt — Python dependencies for this package
  - models/
    - database.py — SQLAlchemy models (User, Patient, Visit, ToothStatus) and DatabaseManager
    - inventory_models.py, expense_models.py — inventory/expense models (used by dashboards and inventory features)
  - services/
    - auth_service.py — authentication and user session
    - patient_service.py — CRUD + search for patients, file handling for X-rays
    - visit_service.py, tooth_service.py, inventory_service.py, invoice_service.py — domain services
    - dashboard_service_real.py — production dashboard data aggregation (SQL-based)
    - dashboard_service.py — legacy/placeholder dashboard service (avoid in production)
    - dashboard_data_service.py — UI-oriented financial data helpers and charts
  - ui/
    - main_window.py + multiple QWidget-based screens (login, patient list/detail/form, visit form, inventory, dashboards)
    - financial_dashboard_widget.py — advanced financial dashboard UI
  - sync_service.py, sync_to_supabase.py — sync utilities (optional)

Key roles
- Models: SQLAlchemy ORM models and DatabaseManager (engine + Session factory)
- Services: business logic; take DatabaseManager, manage sessions, return data structures for UI
- UI: PyQt5 QWidget trees; integrates Matplotlib charts via FigureCanvas; uses signals/slots for interactions
- Entry Point: pyqt_dental_app/main.py orchestrates startup and view routing

## 3. Test Strategy
Testing frameworks and scope
- Use pytest for unit and integration tests
- Use pytest-qt for Qt widgets/signals
- Use an ephemeral SQLite database for tests: either in-memory or a temporary file. Never write to ~/.dentistedb during tests

Structure and conventions
- tests/
  - unit/ — pure logic (services, utilities)
  - integration/ — DB-backed service flows
  - ui/ — Qt widgets, signal wiring, basic rendering smoke tests

Database testing
- Provide a fixture that creates a temp DatabaseManager with a test db_path, calls create_tables(), yields a session, and drops the file after
- Avoid global Session() construction; always use DatabaseManager.get_session() in tests and code
- For service tests, commit/rollback explicitly; assert session.close() behavior and no side effects across tests

UI testing
- Use pytest-qt’s qtbot to instantiate widgets and drive interactions
- Use Matplotlib Agg backend for tests to avoid GUI requirements
- Skip SciPy-specific smoothing paths when SciPy is not available

Mocking and isolation
- Use monkeypatch to inject a test DatabaseManager into services
- For file operations (e.g., X-rays), use tmp_path fixtures. Avoid touching real user folders

Philosophy and coverage
- Unit tests for all service methods (CRUD, validations, error paths)
- Integration tests for common flows (create patient → add visit → compute unpaid)
- UI smoke tests for widget construction, signal connections, and chart update paths
- Target: 
  - 80%+ coverage for services
  - Critical UI flows smoke-tested

## 4. Code Style
General
- Follow PEP 8 and prefer typing annotations for all public methods
- Use docstrings to describe purpose, inputs/outputs, and side effects
- Use logging instead of print for non-UI diagnostics. Avoid verbose logging in the UI thread

Domain naming
- Keep French domain terms consistent with models and UI (e.g., Visit.date, Visit.prix/paye/reste; Patient.nom/prenom)
- Avoid introducing alternate English field names in production code (e.g., visit_date/amount_paid). If refactors are needed, update models/services/UI atomically

Database and sessions
- Always acquire sessions from DatabaseManager.get_session()
- Pattern:
  - session = db_manager.get_session()
  - try: work; session.commit() on changes
  - except: session.rollback(); re-raise or return error
  - finally: session.close()
- Do not instantiate bare Session() without a bound engine
- Avoid holding ORM instances beyond session scope. Prefer returning plain dicts/DTOs to the UI layer where necessary

Error handling
- Catch exceptions at service boundaries, rollback on write errors, and return structured error messages
- Log unexpected exceptions with stack traces; present user-friendly messages in the UI

Money and dates
- Monetary fields currently use Float; avoid arithmetic chaining in UI; format with thousands separators and currency suffix “DH”
- Prefer date-based queries using SQL functions (func.date/DATE range) and consistent timezone handling (dates are naive/local by design)

UI patterns
- Keep heavy work off the UI thread. Use QTimer for periodic refresh; consider threads or workers for longer tasks
- After Matplotlib changes, always call canvas.draw() and keep figure clearing scoped
- Guard optional dependencies (SciPy); keep clean fallbacks

## 5. Common Patterns
- Service classes accept DatabaseManager and encapsulate DB operations
- Consistent try/except/rollback/close around DB writes
- Safe query wrapper pattern (see RealDashboardService._safe_query) to centralize error handling and defaults
- Matplotlib integration using FigureCanvasQTAgg; chart updates via figure.clear() + redraw
- UI widgets expose signals; MainWindow coordinates view switching

## 6. Do's and Don'ts
Do
- Use DatabaseManager.create_tables() at startup to ensure schema exists
- Use DatabaseManager.init_default_user() only on first run; prompt to change default password
- Query only required columns when building lightweight lists to avoid eager relationship loading (pattern used in PatientService)
- Keep model field names consistent across services/UI to avoid runtime errors
- Use @property helpers like Patient.full_name for display
- Isolate file I/O (e.g., X-ray storage) into dedicated service methods with sanitization
- Format amounts in the UI with thousands separators and explicit “DH”

Don't
- Don’t create raw Session() without the project’s DatabaseManager
- Don’t keep ORM objects past session closure (convert to dicts when needed)
- Don’t perform long-running DB/IO in UI thread
- Don’t rely on placeholder/legacy services (dashboard_service.py) for production dashboards; use RealDashboardService
- Don’t write to ~/.dentistedb in tests; always override db_path
- Don’t assume SciPy is present; handle ImportError in visualization code

## 7. Tools & Dependencies
Key libraries
- PyQt5 — UI framework
- SQLAlchemy — ORM and database access (SQLite)
- werkzeug.security — password hashing and verification
- Matplotlib — charting; FigureCanvasQTAgg for Qt integration
- SciPy (optional) — smoothing curves in charts

Setup
- Python 3.x
- Install dependencies:
  - pip install -r requirements_win7.txt (Windows) or
  - pip install -r pyqt_dental_app/requirements.txt
- Run application:
  - python -m pyqt_dental_app.main
  - or: python run_dental_app.py

Database
- SQLite file at ~/.dentistedb/patients.db (created automatically)
- Backups in ~/.dentistedb/backups via DatabaseManager.backup_database()

Security
- Default admin user: mouna/123 (created on first run). Change this immediately via AuthService flows

## 8. Other Notes
- Use RealDashboardService for all financial dashboard data. It aligns with actual model fields (Visit.date/prix/paye/reste)
- When adding new fields/tables, update models and call create_tables() on startup; consider writing a one-off migration utility (Alembic is not currently integrated)
- Keep UI strings French-localized to match current UX
- Ensure Windows 7 compatibility constraints (refer to WINDOWS_7_COMPATIBILITY.md) when adding new dependencies
- For LLM-generated code: maintain services/models/UI separation, use DatabaseManager for sessions, and preserve French domain naming and existing patterns of error handling and formatting