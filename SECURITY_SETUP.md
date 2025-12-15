# 🔐 Configuration Sécurisée - Guide Complet

## Vue d'ensemble

Ce projet utilise un système sécurisé où **aucun mot de passe ou token** n'est stocké dans le code. Tout est géré via des variables d'environnement Vercel.

---

## 🔑 Étape 1: Créer un GitHub Personal Access Token

### 1.1 Générer le Token

1. **Va sur GitHub:** https://github.com/settings/tokens
2. **Clique sur:** "Generate new token" → "Generate new token (classic)"
3. **Nom du token:** `Vercel MP3 Player`
4. **Expiration:** 90 days (ou No expiration si tu préfères)
5. **Sélectionne les permissions suivantes:**
   - ✅ `repo` (Full control of private repositories)
     - Cela inclut: `repo:status`, `repo_deployment`, `public_repo`
   - ✅ `workflow` (Update GitHub Action workflows)

6. **Scroll down** et clique sur **"Generate token"**
7. **⚠️ IMPORTANT:** Copie le token immédiatement (tu ne pourras plus le voir!)
   - Il ressemble à: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 1.2 Sauvegarder temporairement

Copie le token dans un fichier temporaire LOCAL (pas dans le repo!):

```bash
# Créer un fichier LOCAL (PAS dans le repo)
echo "ghp_votre_token_ici" > ~/Desktop/github_token_temp.txt
```

⚠️ **NE JAMAIS commit ce fichier dans Git!**

---

## 🌐 Étape 2: Configurer Vercel

### 2.1 Via le Dashboard Vercel (Recommandé)

1. **Va sur:** https://vercel.com/dashboard
2. **Sélectionne ton projet:** `MP3_CHARLIEOLGA`
3. **Va dans:** Settings → Environment Variables
4. **Ajoute une nouvelle variable:**
   - **Name:** `GITHUB_TOKEN`
   - **Value:** Colle ton token (ghp_xxx...)
   - **Environment:** Cochez **Production**, **Preview**, et **Development**
5. **Clique sur:** "Save"

### 2.2 Via Vercel CLI (Alternative)

```bash
# Installe Vercel CLI si pas déjà fait
npm i -g vercel

# Configure la variable d'environnement
vercel env add GITHUB_TOKEN

# Quand demandé:
# 1. Colle ton token
# 2. Sélectionne: Production, Preview, Development (toutes)
# 3. Confirme
```

---

## 📝 Étape 3: Créer .env.example (pour référence)

Créons un fichier d'exemple (sans valeurs sensibles):

```bash
# .env.example - Fichier de référence (sans vraies valeurs)
GITHUB_TOKEN=ghp_your_token_here
```

Ce fichier peut être commité car il ne contient pas de vraies valeurs.

---

## 🔒 Étape 4: Sécuriser .gitignore

Assurons-nous que les fichiers sensibles ne sont JAMAIS commités:

```gitignore
# Secrets et tokens
.env
.env.local
.env.*.local
*.token
*_token.txt
github_token*

# Python
__pycache__/
*.pyc

# Audio (hosted on GitHub Releases)
audio/
```

---

## ✅ Étape 5: Tester la Configuration

### 5.1 Test Local (Optionnel)

Pour tester localement:

```bash
# Créer .env LOCAL (ne sera pas commité)
echo "GITHUB_TOKEN=ghp_votre_token" > .env

# Installer vercel CLI
npm i -g vercel

# Lancer en mode dev
vercel dev
```

### 5.2 Test en Production

Une fois déployé sur Vercel:

1. Va sur ton site: `https://votre-site.vercel.app`
2. Essaye de télécharger un MP3 depuis YouTube
3. Le système devrait:
   - ✅ Télécharger le MP3
   - ✅ L'uploader sur GitHub Releases
   - ✅ Mettre à jour playlist.json automatiquement

---

## 🔐 Bonnes Pratiques de Sécurité

### ✅ À FAIRE:
- ✅ Utiliser des variables d'environnement Vercel
- ✅ Régénérer le token tous les 90 jours
- ✅ Limiter les permissions au minimum nécessaire
- ✅ Ne jamais commit de fichiers .env
- ✅ Utiliser .env.example pour la documentation

### ❌ À NE JAMAIS FAIRE:
- ❌ Commit des tokens dans le code
- ❌ Partager des tokens par email/chat
- ❌ Utiliser le même token pour plusieurs projets
- ❌ Commit des fichiers .env
- ❌ Mettre des tokens en clair dans les scripts

---

## 🛠️ Étape 6: Vérifier la Configuration

### Vérifier que .gitignore fonctionne:

```bash
cd /Users/josazar/Desktop/MP3_CHARLIEOLGA

# Créer un fichier test avec token
echo "test" > .env

# Vérifier qu'il n'est PAS dans git
git status

# Devrait afficher: "nothing to commit" 
# .env ne doit PAS apparaître!

# Nettoyer
rm .env
```

---

## 📊 Architecture de Sécurité

```
┌─────────────────────┐
│   Utilisateur       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Frontend (Public)  │
└──────────┬──────────┘
           │ POST /api/download
           ▼
┌─────────────────────┐
│  Vercel Serverless  │
│  Environment Vars:  │
│  GITHUB_TOKEN (🔒)  │ ← Token sécurisé, jamais exposé
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   GitHub API        │
│   Releases Upload   │
└─────────────────────┘
```

**Le token n'est JAMAIS exposé au client!**

---

## 🆘 Dépannage

### "GITHUB_TOKEN not set"
→ Vérifie que la variable est bien configurée sur Vercel  
→ Redéploie après avoir ajouté la variable

### "Permission denied" lors de l'upload
→ Vérifie que le token a bien la permission `repo`  
→ Régénère un nouveau token si nécessaire

### Token compromis?
1. **Révoque immédiatement** le token sur GitHub
2. **Génère un nouveau** token
3. **Met à jour** la variable sur Vercel
4. **Redéploie** l'application

---

## 📝 Checklist de Sécurité

Avant de déployer:

- [ ] Token GitHub créé avec permissions minimales
- [ ] Variable GITHUB_TOKEN configurée sur Vercel
- [ ] .gitignore contient `.env` et fichiers sensibles
- [ ] Aucun token dans le code source
- [ ] .env.example créé (sans vraies valeurs)
- [ ] Test effectué en local
- [ ] Déployé et testé en production

---

## 🎉 C'est Prêt!

Une fois ces étapes complétées, ton application est **sécurisée et prête à l'emploi**!

Le feature de download fonctionnera sur Vercel sans exposer aucune information sensible! 🔐

