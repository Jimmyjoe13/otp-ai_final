# Déploiement Opt-AI sur Railway

Ce document explique comment déployer l'application Opt-AI sur la plateforme Railway.

## Prérequis

- Un compte Railway
- Railway CLI installé (facultatif)
- Git

## Configuration

L'application est configurée pour être déployée sur Railway via Docker. Les fichiers suivants ont été créés/modifiés pour faciliter le déploiement :

- `Dockerfile` : Image Docker basée sur Python 3.10-slim
- `requirements-railway.txt` : Liste des dépendances Python pour l'application
- `railway.json` : Configuration de déploiement Railway
- `.dockerignore` : Liste des fichiers/dossiers à exclure de l'image Docker
- `health.py` : Endpoint de santé pour vérifier l'état de l'application

## Variables d'environnement requises

Configurez les variables d'environnement suivantes dans votre projet Railway :

### Variables obligatoires :
- `DATABASE_URL` : URL de connexion à la base de données PostgreSQL
- `SESSION_SECRET` : Clé secrète pour les sessions et JWT
- `OPENAI_API_KEY` : Clé API OpenAI pour les fonctionnalités d'IA

### Variables optionnelles (pour les paiements Stripe) :
- `STRIPE_SECRET_KEY` : Clé secrète Stripe pour le traitement des paiements
- `STRIPE_BASIC_PRICE_ID` : ID de prix Stripe pour le plan Basic
- `STRIPE_PREMIUM_PRICE_ID` : ID de prix Stripe pour le plan Premium
- `STRIPE_ENTERPRISE_PRICE_ID` : ID de prix Stripe pour le plan Enterprise

## Déploiement

### Option 1 : Déploiement depuis l'interface web Railway

1. Créez un nouveau projet sur Railway
2. Liez votre dépôt Git contenant le code de l'application
3. Railway détectera automatiquement le Dockerfile et construira l'image
4. Configurez les variables d'environnement nécessaires
5. Railway démarrera automatiquement l'application sur le port spécifié

### Option 2 : Déploiement avec Railway CLI

1. Connectez-vous à Railway : `railway login`
2. Initialisez le projet : `railway init`
3. Liez le projet : `railway link`
4. Déployez l'application : `railway up`

## Base de données PostgreSQL

Railway fournit une instance PostgreSQL que vous pouvez facilement ajouter à votre projet :

1. Dans l'interface web Railway, cliquez sur "New"
2. Sélectionnez "Database" puis "PostgreSQL"
3. Railway configurera automatiquement la variable d'environnement `DATABASE_URL`

## Surveillance de l'application

L'application dispose d'un endpoint de santé `/health` qui renvoie l'état de l'application et de la connexion à la base de données. Railway utilise cet endpoint pour surveiller l'état de l'application.

## Architecture

- L'application est servie par Gunicorn sur le port défini par la variable d'environnement `$PORT` (fournie par Railway)
- La base de données PostgreSQL est connectée via la variable d'environnement `DATABASE_URL`
- L'application est accessible via le domaine fourni par Railway