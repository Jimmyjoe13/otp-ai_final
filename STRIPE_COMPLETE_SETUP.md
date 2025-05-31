# 💳 Configuration Complète Stripe pour Opt-AI - Guide Détaillé

## 🎯 Variables Stripe Nécessaires

Votre SaaS a besoin de ces variables Stripe :

```bash
STRIPE_SECRET_KEY=sk_test_... ou sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_BASIC_PRICE_ID=price_...
STRIPE_PREMIUM_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...
```

## 📋 Étape 1 : Récupérer STRIPE_SECRET_KEY

### Mode Test (Développement)
1. Allez sur https://dashboard.stripe.com
2. Assurez-vous d'être en mode **"Test"** (toggle en haut à droite)
3. Menu **"Developers"** → **"API keys"**
4. Copiez la **"Secret key"** qui commence par `sk_test_...`

### Mode Live (Production)
1. Basculez en mode **"Live"** 
2. Menu **"Developers"** → **"API keys"**
3. Copiez la **"Secret key"** qui commence par `sk_live_...`

## 💰 Étape 2 : Créer les Produits et Prix

### 2.1 Créer le Plan Basic (19€/mois)

1. Menu **"Products"** → **"Add product"**
2. **Nom :** "Basic Plan"
3. **Description :** "Great for bloggers and small websites"
4. **Pricing model :** "Standard pricing"
5. **Price :** 19.00 EUR
6. **Billing period :** Monthly
7. **Metadata :** Ajoutez `plan: basic`
8. Cliquez **"Save product"**
9. **Copiez l'ID du prix** (commence par `price_...`)

### 2.2 Créer le Plan Premium (49€/mois)

1. **"Add product"**
2. **Nom :** "Premium Plan"  
3. **Description :** "Perfect for businesses and marketing teams"
4. **Price :** 49.00 EUR
5. **Billing period :** Monthly
6. **Metadata :** `plan: premium`
7. **Copiez l'ID du prix**

### 2.3 Créer le Plan Enterprise (149€/mois)

1. **"Add product"**
2. **Nom :** "Enterprise Plan"
3. **Description :** "For agencies and large enterprise websites"  
4. **Price :** 149.00 EUR
5. **Billing period :** Monthly
6. **Metadata :** `plan: enterprise`
7. **Copiez l'ID du prix**

## 🔗 Étape 3 : Configurer le Webhook

Suivez le guide `STRIPE_WEBHOOK_SETUP.md` pour obtenir `STRIPE_WEBHOOK_SECRET`.

## ⚙️ Étape 4 : Configuration Railway

Ajoutez toutes ces variables dans Railway :

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51ABC...  # ou sk_live_ pour production
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef...

# Stripe Price IDs
STRIPE_BASIC_PRICE_ID=price_1ABC123def456...
STRIPE_PREMIUM_PRICE_ID=price_1DEF456ghi789...
STRIPE_ENTERPRISE_PRICE_ID=price_1GHI789jkl012...
```

## 🧪 Étape 5 : Test de Configuration

### Test Automatique des Produits

Votre application peut créer automatiquement les produits Stripe. Accédez à :

```
https://votre-app.railway.app/payment/init-products
```

**Note :** Cette route nécessite d'être connecté en tant qu'admin (user ID 1).

### Test Manuel

1. **Créer un compte test** sur votre app
2. **Aller sur la page pricing** 
3. **Cliquer sur un plan** → doit rediriger vers Stripe Checkout
4. **Utiliser une carte test :** `4242 4242 4242 4242`
5. **Vérifier** que le paiement est traité

## 💳 Cartes de Test Stripe

```bash
# Carte qui fonctionne
4242 4242 4242 4242

# Carte déclinée  
4000 0000 0000 0002

# Carte nécessitant 3D Secure
4000 0025 0000 3155

# Date d'expiration : n'importe quelle date future
# CVC : n'importe quel code 3 chiffres
```

## 🔄 Étape 6 : Migration Test → Production

### Quand passer en production :

1. **Tests complets** effectués en mode test
2. **Webhooks** fonctionnels 
3. **Tous les plans** créés et testés
4. **Application** déployée et stable

### Migration :

1. **Créer les mêmes produits** en mode Live
2. **Récupérer les nouveaux Price IDs** 
3. **Créer un nouveau webhook** en mode Live
4. **Mettre à jour** toutes les variables Railway avec les clés Live

## 📊 Monitoring et Logs

### Vérifier les Paiements
- **Stripe Dashboard** → **"Payments"**
- **Railway Logs** pour les webhooks
- **Votre base de données** pour les souscriptions

### Logs Importants
```bash
# Railway logs à surveiller
"Stripe checkout error"
"Error processing successful payment" 
"Webhook error"
"DeepSeek client initialized successfully"
```

## 🚨 Sécurité et Bonnes Pratiques

### ✅ À Faire :
- Utiliser HTTPS uniquement
- Ne jamais exposer les clés secrètes
- Valider tous les webhooks
- Logger les erreurs importantes
- Tester régulièrement les paiements

### ❌ À Éviter :
- Clés secrètes dans le code
- Webhooks non sécurisés  
- Tests en production
- Ignorer les erreurs de paiement

## 🆘 Dépannage Courant

### Erreur "No such price"
- Vérifiez que les `STRIPE_PRICE_ID` sont corrects
- Assurez-vous d'être dans le bon mode (Test/Live)

### Webhook 401/403
- Secret webhook incorrect
- Vérifiez `STRIPE_WEBHOOK_SECRET`

### Paiement non traité
- Vérifiez les logs Railway
- Consultez les événements Stripe
- Vérifiez la base de données

### Redirection échoue
- Vérifiez la variable `DOMAIN`
- URL de succès/annulation correctes

## 📞 Support

Si vous rencontrez des problèmes :
1. **Logs Railway** : Consultez les erreurs
2. **Stripe Dashboard** : Vérifiez les événements
3. **Base de données** : Vérifiez les enregistrements
4. **Variables d'environnement** : Validez toutes les clés
