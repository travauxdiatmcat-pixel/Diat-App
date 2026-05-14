# DIAT — Application Web Streamlit

## Lancement local (test)

```bash
pip install streamlit Pillow
streamlit run app.py
```
Ouvrez http://localhost:8501 dans votre navigateur.

---

## 🚀 Déploiement en ligne — Streamlit Community Cloud (GRATUIT)

### Étape 1 — Préparer GitHub

1. Créez un compte sur https://github.com (gratuit)
2. Créez un nouveau dépôt public nommé `diat-app`
3. Uploadez tous ces fichiers dedans :
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `data/chantiers.json`

### Étape 2 — Déployer sur Streamlit Cloud

1. Allez sur https://share.streamlit.io
2. Connectez-vous avec votre compte GitHub
3. Cliquez **"New app"**
4. Sélectionnez votre dépôt `diat-app`
5. Fichier principal : `app.py`
6. Cliquez **"Deploy"**

✅ En 2 minutes, vous obtenez un lien public du type :
`https://votre-nom-diat-app.streamlit.app`

Partagez ce lien avec votre supérieur — il peut l'ouvrir sur son téléphone !

---

## 🔒 Rendre l'app privée (accès par mot de passe)

Ajoutez ce code au début de `app.py` :

```python
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

# Dans requirements.txt, ajoutez : streamlit-authenticator
```

Ou plus simplement, dans Streamlit Cloud, allez dans
**Settings → Sharing → Viewer authentication** pour restreindre l'accès.

---

## 📁 Structure des fichiers

```
DIAT_Web/
├── app.py                  ← Application principale
├── requirements.txt        ← Dépendances Python
├── .streamlit/
│   └── config.toml         ← Thème et configuration
├── data/
│   └── chantiers.json      ← Base de données
└── images/
    └── {id_visite}/        ← Photos uploadées
```

## ⚠️ Note sur les images

Sur Streamlit Cloud (gratuit), les images uploadées sont **temporaires** —
elles disparaissent si l'app redémarre. Pour un stockage permanent des images,
utilisez un service comme Cloudinary (gratuit jusqu'à 25 Go) ou AWS S3.
Les données JSON (chantiers, visites) sont sauvegardées dans le dépôt GitHub.
