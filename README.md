# DockVault – Analyse intelligente de documents administratifs

## Présentation

DockVault est une application web permettant d’analyser automatiquement des documents administratifs (factures, devis, attestations de SIRET, etc.).

Grâce à un système d’OCR performant, l’application est capable de :
- Lire des documents même flous ou déformés
- Extraire les informations importantes
- Classer automatiquement les documents
- Détecter des erreurs ou incohérences dans les données

## Repository

Projet disponible sur GitHub :  
https://github.com/nicolasdraperi/hackaton-23

Nom du repository : hackaton-23

---

## Architecture Docker

Le projet est composé de deux services :

- backend (Python / Django)
- frontend (React + Vite)

Le tout est orchestré avec Docker Compose.

---

## Prérequis

Avant de lancer le projet, assurez-vous d’avoir installé :

- Docker
- Docker Compose

---

## Configuration requise

Un fichier `.env` doit obligatoirement être présent à la racine du projet.

Exemple de contenu :

MONGO_URI=mongodb+srv://...

Ce fichier est nécessaire pour permettre au backend de se connecter à la base de données MongoDB.

---

## Lancement du projet

Depuis la racine du projet, exécuter :

docker-compose up --build

---

## Accès à l’application

- Frontend : http://localhost:5173  
- Backend API : http://localhost:8000/api

---

## Structure des services

### Backend (Python 3.12)

- Framework : Django
- Port : 8000
- Dépendances système :
  - poppler-utils
  - libgl1
  - libglib2.0-0

Commande de lancement :

python manage.py runserver 0.0.0.0:8000

---

### Frontend (Node 19)

- Framework : React + Vite
- Port : 5173

Commande de lancement :

npm run dev -- --host

---

## Variables d’environnement

### Backend
- MONGO_URI : URI de connexion à MongoDB

### Frontend
- VITE_API_URL=http://localhost:8000/api

---

## Volumes

Les dossiers locaux sont montés dans les conteneurs pour permettre le développement en temps réel :

- ./docvault → /app
- ./docvault-react → /app

---

## Fonctionnalités principales

- OCR Via Easy-OCR
- Extraction automatique de données
- Vérification d’incohérences
- Classification des documents
- Interface web simple et rapide

---

## Développement

Les modifications dans les dossiers locaux sont automatiquement prises en compte grâce aux volumes Docker.

---

## Licence

Projet réalisé dans le cadre d’un hackathon.
