# 🔗 Configuration du Webhook Stripe - Guide Complet

## Étape 1 : Accéder au tableau de bord Stripe

1. Connectez-vous à votre compte Stripe : https://dashboard.stripe.com
2. Assurez-vous d'être en mode **Test** ou **Live** selon vos besoins

## Étape 2 : Créer un Webhook

1. Dans le menu de gauche, cliquez sur **"Developers"** (Développeurs)
2. Cliquez sur **"Webhooks"**
3. Cliquez sur **"Add endpoint"** (Ajouter un point de terminaison)

## Étape 3 : Configurer l'URL du Webhook

**URL du Webhook :**
```
https://votre-app.railway.app/payment/webhook
```

Remplacez `votre-app` par le nom de votre application Railway.

## Étape 4 : Sélectionner les Événements

Sélectionnez ces événements essentiels pour votre SaaS :

### Événements de Souscription :
- ✅ `customer.subscription.created`
- ✅ `customer.subscription.updated` 
- ✅ `customer.subscription.deleted`
- ✅ `customer.subscription.trial_will_end`

### Événements de Paiement :
- ✅ `invoice.payment_succeeded`
- ✅ `invoice.payment_failed`
- ✅ `invoice.finalized`

### Événements de Checkout :
- ✅ `checkout.session.completed`
- ✅ `checkout.session.expired`

### Événements Client :
- ✅ `customer.created`
- ✅ `customer.updated`
- ✅ `customer.deleted`

## Étape 5 : Récupérer le Secret du Webhook

1. Après avoir créé le webhook, cliquez dessus dans la liste
2. Dans la section **"Signing secret"**, cliquez sur **"Reveal"**
3. Copiez la clé qui commence par `whsec_...`

**Exemple :**
```
whsec_1234567890abcdef1234567890abcdef12345678
```

## Étape 6 : Configuration dans Railway

Dans votre projet Railway, ajoutez cette variable d'environnement :

```bash
STRIPE_WEBHOOK_SECRET=whsec_votre_secret_ici
```

## Étape 7 : Test du Webhook

### Option 1 : Test depuis Stripe Dashboard
1. Dans votre webhook, cliquez sur **"Send test webhook"**
2. Sélectionnez un événement (ex: `invoice.payment_succeeded`)
3. Cliquez sur **"Send test webhook"**

### Option 2 : Test avec Stripe CLI (Optionnel)
```bash
# Installer Stripe CLI
stripe listen --forward-to localhost:5000/payment/webhook

# Dans un autre terminal
stripe trigger payment_intent.succeeded
```

## 🔒 Sécurité Important

### Variables d'Environnement Stripe Complètes :

```bash
# Clés Stripe (Mode Test)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Clés Stripe (Mode Live - Production)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### ⚠️ Points Importants :

1. **Ne jamais** exposer ces clés dans votre code
2. Utilisez des clés **Test** pendant le développement
3. Passez aux clés **Live** seulement en production
4. Le webhook secret est différent pour chaque endpoint

## 🧪 Vérification du Webhook

Votre application a déjà le code pour gérer les webhooks dans `payment.py`. 

Une fois configuré, vous pouvez tester :
1. Créer un paiement test
2. Vérifier les logs Railway
3. Confirmer que les événements sont reçus

## 📋 Checklist Final

- [ ] Webhook créé dans Stripe Dashboard
- [ ] URL correcte : `https://votre-app.railway.app/payment/webhook`
- [ ] Événements sélectionnés
- [ ] Secret récupéré (`whsec_...`)
- [ ] Variable `STRIPE_WEBHOOK_SECRET` ajoutée dans Railway
- [ ] Test du webhook effectué

## 🆘 Dépannage

### Webhook ne fonctionne pas ?
1. Vérifiez l'URL (doit être accessible publiquement)
2. Vérifiez que Railway est déployé
3. Consultez les logs Stripe et Railway
4. Vérifiez que le secret est correct

### Erreur 401/403 ?
- Le secret webhook est probablement incorrect
- Vérifiez la variable d'environnement

### Erreur 404 ?
- L'URL du webhook est incorrecte
- Vérifiez que `/payment/webhook` existe dans votre app
