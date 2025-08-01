# 📊 Tableaux de Bord - DentisteDB

## Vue d'ensemble

Le système de tableaux de bord de DentisteDB offre une vue complète et interactive des performances de votre cabinet dentaire. Il comprend trois dashboards principaux accessibles via un système d'onglets moderne.

## 🚀 Installation

### Dépendances requises

```bash
pip install -r dashboard_requirements.txt
```

Les packages suivants sont nécessaires :
- `matplotlib>=3.5.0` - Pour les graphiques
- `numpy>=1.21.0` - Pour les calculs statistiques

## 📋 Dashboards Disponibles

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

## 🔧 Architecture Technique

### Structure des fichiers

```
ui/
├── main_dashboard_widget.py      # Container principal avec onglets
├── dashboard_widget.py           # Dashboard vue d'ensemble
├── financial_dashboard_widget.py # Dashboard financier
└── patient_dashboard_widget.py   # Dashboard patients

services/
└── dashboard_service.py          # Service de données pour dashboards
```

### Classes principales

#### `MainDashboardWidget`
- Container principal avec système d'onglets
- Gestion de l'actualisation automatique
- Fonctions d'export et paramètres
- Intégration avec la fenêtre principale

#### `DashboardService`
- Agrégation des données depuis tous les services
- Calculs statistiques et KPIs
- Méthodes pour tendances et analyses
- Interface unifiée pour les données

## 🎨 Personnalisation

### Couleurs et thèmes
Les dashboards utilisent une palette de couleurs cohérente :
- **Bleu** (#3498db) : Informations générales
- **Vert** (#2ecc71) : Revenus et croissance positive
- **Rouge** (#e74c3c) : Alertes et décroissance
- **Orange** (#f39c12) : Avertissements et métriques neutres
- **Violet** (#9b59b6) : Patients et données spécialisées

### Ajout de nouveaux widgets
Pour ajouter un nouveau dashboard :

1. Créer le widget dans `ui/`
2. L'ajouter au `MainDashboardWidget`
3. Mettre à jour le `DashboardService` si nécessaire

```python
# Exemple d'ajout d'un dashboard personnalisé
custom_dashboard = CustomDashboardWidget()
main_dashboard.add_custom_dashboard(custom_dashboard, "🔧 Personnalisé")
```

## 📊 Utilisation

### Accès aux dashboards
1. **Via le menu** : Affichage → 📊 Tableaux de Bord (Ctrl+D)
2. **Via la toolbar** : Cliquer sur "📊 Tableau de Bord"

### Navigation
- **Onglets** : Cliquer sur les onglets pour changer de vue
- **Actualisation** : Bouton "🔄 Actualiser" ou automatique
- **Export** : Bouton "📊 Exporter" pour sauvegarder les données
- **Paramètres** : Bouton "⚙️ Paramètres" pour configurer

### Fonctionnalités avancées

#### Export des données
```json
{
  "export_date": "2025-07-27T20:53:15",
  "summary": {
    "patients": {...},
    "financial": {...},
    "treatments": {...}
  },
  "kpis": {...}
}
```

#### Paramètres configurables
- Intervalle d'actualisation automatique
- Activation/désactivation des dashboards
- Préférences d'affichage

## 🔄 Actualisation des données

### Automatique
- **Intervalle par défaut** : 10 minutes
- **Configurable** : 1-60 minutes via les paramètres

### Manuelle
- **Bouton global** : Actualise tous les dashboards
- **Par onglet** : Actualisation lors du changement d'onglet
- **Méthode** : `refresh_all_dashboards()`

## 🐛 Dépannage

### Erreurs communes

#### Dashboard ne se charge pas
```
Erreur lors du chargement des tableaux de bord
```
**Solution :** Vérifier que matplotlib est installé

#### Données manquantes
**Cause :** Services non initialisés
**Solution :** Vérifier les connexions aux services dans `main_window.py`

#### Graphiques ne s'affichent pas
**Cause :** Problème avec matplotlib backend
**Solution :** 
```python
import matplotlib
matplotlib.use('Qt5Agg')
```

### Logs de débogage
Les dashboards incluent des logs détaillés :
```python
print("Dashboard widget created and added successfully")
print("Refreshing all dashboards...")
```

## 🚀 Améliorations futures

### Fonctionnalités prévues
- [ ] Dashboard d'inventaire intégré
- [ ] Graphiques interactifs avec zoom
- [ ] Notifications en temps réel
- [ ] Export PDF des rapports
- [ ] Comparaisons période à période
- [ ] Prédictions basées sur l'IA

### Intégrations possibles
- [ ] Système de notifications push
- [ ] API REST pour données externes
- [ ] Synchronisation cloud
- [ ] Rapports automatisés par email

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs de la console
2. Consulter cette documentation
3. Vérifier les dépendances installées
4. Tester avec des données d'exemple

---

**Version :** 1.0  
**Dernière mise à jour :** 27/07/2025  
**Compatibilité :** PyQt5, Python 3.7+
