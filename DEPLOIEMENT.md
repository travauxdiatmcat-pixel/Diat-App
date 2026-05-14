# DIAT — Guide de déploiement

## Mot de passe admin par défaut : 123
## ⚠️ CHANGEZ-LE avant de déployer (voir section ci-dessous)

---

## ÉTAPE 1 — Changer votre mot de passe admin

Ouvrez un terminal et tapez :
```
python3 -c "import hashlib; print(hashlib.sha256(b'VotreNouveauMotDePasse').hexdigest())"
```
Copiez le résultat et remplacez la ligne dans app.py :
```python
MOT_DE_PASSE_HASH = "collez_votre_hash_ici"
```

---

## ÉTAPE 2 — Mettre les fichiers sur GitHub

1. Créez un compte sur https://github.com (gratuit)
2. Créez un nouveau dépôt public nommé `diat-app`
3. Uploadez ces fichiers :
   - app.py
   - requirements.txt
   - .streamlit/config.toml
   - data/chantiers.json

---

## ÉTAPE 3 — Déployer sur Streamlit Cloud (gratuit)

1. Allez sur https://share.streamlit.io
2. Connectez-vous avec GitHub
3. Cliquez "New app"
4. Sélectionnez votre dépôt `diat-app`, fichier : app.py
5. Cliquez "Deploy"

✅ Vous obtenez un lien du type :
   https://votre-nom-diat-app.streamlit.app

---

## ÉTAPE 4 — Partager avec votre supérieur

Envoyez-lui simplement le lien. Il verra :
- 👁 Badge "Lecture seule" dans la sidebar
- Toutes les données, chantiers, visites, images
- Aucun bouton de modification visible

---

## ÉTAPE 5 — Faire des mises à jour

### Option A — Via GitHub (recommandée)
1. Modifiez data/chantiers.json sur votre PC
2. git push → l'app se met à jour automatiquement en 30 secondes

### Option B — Via l'interface web (connecté admin)
1. Ouvrez le lien
2. Dans la sidebar, dépliez "🔒 Connexion admin"
3. Entrez votre mot de passe
4. Vous voyez maintenant tous les boutons d'édition
5. Faites vos modifications → elles sont sauvegardées

---

## Structure des fichiers

```
DIAT_Deploy/
├── app.py                 ← Application avec auth
├── requirements.txt       ← streamlit + Pillow
├── .streamlit/
│   └── config.toml        ← Thème sombre
└── data/
    └── chantiers.json     ← 16 chantiers
```

## Deux rôles dans l'application

| Rôle          | Accès                                      |
|---------------|--------------------------------------------|
| 👁 Visiteur   | Voir tout, aucune modification possible    |
| 🔑 Admin (vous)| Voir + ajouter/modifier/supprimer tout    |
