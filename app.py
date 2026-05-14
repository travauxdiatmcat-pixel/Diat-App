"""
DIAT — Diagnostic d'Inspection et d'Audit de Terrain
Application Web Streamlit — avec authentification admin / lecture seule
"""

import streamlit as st
import json, os, datetime, hashlib
from pathlib import Path

st.set_page_config(
    page_title="DIAT — Inspection & Audit",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR  = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "chantiers.json"
IMG_DIR   = BASE_DIR / "images"
for d in [BASE_DIR / "data", IMG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Mot de passe par défaut : 123  (changez le hash pour un vrai mot de passe)
# python3 -c "import hashlib; print(hashlib.sha256(b'VotreMotDePasse').hexdigest())"
MDP_HASH = "fbb76d992f06eb7b508f384982031656c9917a21279a8616e9033eb58d4dacf0"

STATUTS  = ["Non démarré", "En cours", "Terminé", "Suspendu"]
ETATS    = ["Bon", "Moyen", "Mauvais"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root{--accent:#00c8aa;--accent2:#0096ff;--bg-card:#1e2d40;
      --bg-panel:#172030;--border:#2a3f58;--danger:#ff4d6d;
      --warning:#ffb347;--success:#00c8aa;--text-sub:#7a9bbf;}
.card{background:var(--bg-card);border:1px solid var(--border);
      border-radius:12px;padding:16px 20px;margin-bottom:10px;}
.card:hover{border-color:var(--accent);}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;}
.badge-bon      {background:#0d3d2e;color:#00c8aa;}
.badge-moyen    {background:#3d2b0d;color:#ffb347;}
.badge-mauvais  {background:#3d0d1a;color:#ff4d6d;}
.badge-encours  {background:#0d2d3d;color:#0096ff;}
.badge-termine  {background:#0d3d2e;color:#00c8aa;}
.badge-suspendu {background:#3d2b0d;color:#ffb347;}
.badge-nondmarre{background:#222;color:#888;}
.info-row{display:flex;gap:24px;flex-wrap:wrap;background:var(--bg-card);
          border-radius:10px;padding:12px 18px;margin-bottom:12px;
          border:1px solid var(--border);}
.info-item label{font-size:11px;color:var(--text-sub);display:block;}
.info-item span{font-size:14px;}
.metric-card{background:var(--bg-card);border:1px solid var(--border);
             border-radius:12px;padding:20px;text-align:center;}
.metric-value{font-size:2.4em;font-weight:700;line-height:1.1;}
.metric-label{font-size:.85em;color:var(--text-sub);margin-top:4px;}
.progress-bar-bg{background:var(--border);border-radius:4px;height:8px;
                 width:100%;overflow:hidden;margin:4px 0;}
.progress-bar-fill{height:100%;border-radius:4px;}
.ro-banner{background:#1a1a2e;border:1px solid #2a3f58;border-radius:10px;
           padding:10px 18px;margin-bottom:14px;color:#7a9bbf;font-size:13px;}
section[data-testid="stSidebar"]{background:var(--bg-panel)!important;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════

def est_admin():
    return st.session_state.get("admin", False)

def check_mdp(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest() == MDP_HASH

# ═══════════════════════════════════════════════════════════════════════
# DONNÉES
# ═══════════════════════════════════════════════════════════════════════

def charger():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"chantiers": []}

def sauvegarder(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_data():
    if "data" not in st.session_state:
        st.session_state.data = charger()
    return st.session_state.data

def nid(p="ID"):
    return f"{p}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def b_statut(s):
    cls = {"En cours":"encours","Terminé":"termine",
           "Suspendu":"suspendu","Non démarré":"nondmarre"}.get(s,"nondmarre")
    return f'<span class="badge badge-{cls}">{s}</span>'

def b_etat(e):
    cls = {"Bon":"bon","Moyen":"moyen","Mauvais":"mauvais"}.get(e,"moyen")
    return f'<span class="badge badge-{cls}">{e}</span>'

def bandeau():
    if not est_admin():
        st.markdown('<div class="ro-banner">👁 <strong>Mode consultation</strong> — '
                    'Vous visualisez en lecture seule.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# FORMULAIRE CHANTIER  (dans un dialog Streamlit 1.32+)
# ═══════════════════════════════════════════════════════════════════════

def form_chantier(edit_c=None):
    """Affiche le formulaire chantier. edit_c=None → création, sinon modification."""
    titre = "✏️ Modifier le chantier" if edit_c else "➕ Nouveau chantier"
    st.subheader(titre)

    with st.form(key="form_chantier_principal", clear_on_submit=False):
        nom   = st.text_input("Nom du chantier  *",
                              value=edit_c.get("nom","") if edit_c else "")
        loc   = st.text_input("Localisation  *",
                              value=edit_c.get("localisation","") if edit_c else "")

        c1, c2 = st.columns(2)
        entr  = c1.text_input("Entreprise",
                               value=edit_c.get("entreprise","") if edit_c else "")
        resp  = c2.text_input("Responsable",
                               value=edit_c.get("responsable","") if edit_c else "")

        c3, c4 = st.columns(2)
        trav  = c3.text_input("Type de travaux",
                               value=edit_c.get("type_travaux","") if edit_c else "")
        grp   = c4.text_input("Groupe / Site",
                               value=edit_c.get("groupe","") if edit_c else "")

        c5, c6 = st.columns(2)
        dd    = c5.text_input("Date de début  (JJ/MM/AAAA)",
                               value=edit_c.get("date_debut","") if edit_c else "")
        df    = c6.text_input("Date de fin prévue  (JJ/MM/AAAA)",
                               value=edit_c.get("date_fin","") if edit_c else "")

        val_statut = (edit_c.get("statut","Non démarré") if edit_c else "Non démarré")
        if val_statut not in STATUTS:
            val_statut = "Non démarré"
        statut = st.selectbox("Statut  *", STATUTS, index=STATUTS.index(val_statut))

        obs = st.text_area("Observations",
                           value=edit_c.get("observations","") if edit_c else "",
                           height=90)

        st.markdown("---")
        col_ok, col_ann = st.columns(2)
        submit  = col_ok.form_submit_button(
            "✔ Enregistrer", type="primary", use_container_width=True)
        annuler = col_ann.form_submit_button(
            "✖ Annuler", use_container_width=True)

    # Traitement après soumission
    if submit:
        if not nom.strip():
            st.error("Le nom du chantier est obligatoire.")
            return
        if not loc.strip():
            st.error("La localisation est obligatoire.")
            return
        data = get_data()
        obj = {"nom":nom.strip(), "localisation":loc.strip(),
               "entreprise":entr.strip(), "responsable":resp.strip(),
               "type_travaux":trav.strip(), "groupe":grp.strip(),
               "date_debut":dd.strip(), "date_fin":df.strip(),
               "statut":statut, "observations":obs.strip()}
        if edit_c:
            for c in data["chantiers"]:
                if c["id"] == edit_c["id"]:
                    c.update(obj)
                    break
        else:
            obj["id"]      = nid("CH")
            obj["visites"] = []
            data["chantiers"].append(obj)
        sauvegarder(data)
        st.session_state.data = data
        st.session_state.page_mode = "liste"
        st.success("✔ Chantier enregistré avec succès !")
        st.rerun()

    if annuler:
        st.session_state.page_mode = "liste"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# FORMULAIRE VISITE
# ═══════════════════════════════════════════════════════════════════════

def form_visite(chantier, edit_v=None):
    """Formulaire visite inline."""
    titre = "✏️ Modifier la visite" if edit_v else "➕ Nouvelle visite"
    st.subheader(titre)

    with st.form(key="form_visite_principal", clear_on_submit=False):
        c1, c2 = st.columns(2)
        date_v = c1.text_input(
            "Date  *  (JJ/MM/AAAA)",
            value=edit_v.get("date", datetime.date.today().strftime("%d/%m/%Y")) if edit_v
            else datetime.date.today().strftime("%d/%m/%Y"))
        insp   = c2.text_input(
            "Inspecteur  *",
            value=edit_v.get("inspecteur","") if edit_v else "")

        c3, c4 = st.columns(2)
        val_etat = edit_v.get("etat","Moyen") if edit_v else "Moyen"
        if val_etat not in ETATS: val_etat = "Moyen"
        etat_v = c3.selectbox("État général  *", ETATS, index=ETATS.index(val_etat))
        note_v = c4.text_input("Note (/10)",
                               value=edit_v.get("note","") if edit_v else "")

        obs_v  = st.text_area("Observations",
                              value=edit_v.get("observations","") if edit_v else "",
                              height=130)

        st.markdown("---")
        col_ok, col_ann = st.columns(2)
        submit  = col_ok.form_submit_button(
            "✔ Enregistrer", type="primary", use_container_width=True)
        annuler = col_ann.form_submit_button(
            "✖ Annuler", use_container_width=True)

    if submit:
        if not date_v.strip():
            st.error("La date est obligatoire.")
            return
        if not insp.strip():
            st.error("L'inspecteur est obligatoire.")
            return
        data   = get_data()
        # Retrouver le chantier dans les données fraîches
        ch_ref = next((c for c in data["chantiers"] if c["id"]==chantier["id"]), None)
        if ch_ref is None:
            st.error("Chantier introuvable.")
            return
        new_v  = {"id": edit_v["id"] if edit_v else nid("V"),
                  "date":date_v.strip(), "inspecteur":insp.strip(),
                  "etat":etat_v, "note":note_v.strip(),
                  "observations":obs_v.strip(),
                  "images": edit_v.get("images",[]) if edit_v else []}
        if edit_v:
            ch_ref["visites"] = [new_v if v["id"]==edit_v["id"] else v
                                 for v in ch_ref.get("visites",[])]
        else:
            ch_ref.setdefault("visites",[]).append(new_v)
        sauvegarder(data)
        st.session_state.data     = data
        st.session_state.visite_mode = "liste"
        st.success("✔ Visite enregistrée !")
        st.rerun()

    if annuler:
        st.session_state.visite_mode = "liste"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# PAGE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════

def page_dashboard():
    bandeau()
    st.title("📊 Tableau de bord")
    st.caption(f"Mis à jour le {datetime.datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    st.markdown("---")

    data      = get_data()
    chantiers = data.get("chantiers",[])
    total_v   = sum(len(c.get("visites",[])) for c in chantiers)
    total_i   = sum(len(v.get("images",[])) for c in chantiers for v in c.get("visites",[]))
    notes     = [float(v["note"]) for c in chantiers for v in c.get("visites",[])
                 if v.get("note","").replace(".","",1).isdigit()]
    moy       = f"{sum(notes)/len(notes):.1f}" if notes else "—"

    c1,c2,c3,c4 = st.columns(4)
    for col,icon,val,label,color in [
        (c1,"🏗",len(chantiers),"Chantiers","#00c8aa"),
        (c2,"🔍",total_v,       "Visites",  "#0096ff"),
        (c3,"🖼",total_i,       "Images",   "#ffb347"),
        (c4,"⭐",moy,           "Note moy.","#00c8aa"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div style="font-size:2em">{icon}</div>
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([1,2])

    with cl:
        st.subheader("Par statut")
        statuts = {}
        for c in chantiers:
            s = c.get("statut","—"); statuts[s] = statuts.get(s,0)+1
        colors = {"En cours":"#0096ff","Terminé":"#00c8aa",
                  "Suspendu":"#ffb347","Non démarré":"#7a9bbf"}
        for s,n in statuts.items():
            pct = int(n/len(chantiers)*100) if chantiers else 0
            col = colors.get(s,"#7a9bbf")
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;font-size:13px">
                    <span>{s}</span><span style="color:{col};font-weight:600">{n}</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{pct}%;background:{col}"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with cr:
        st.subheader("Dernières visites")
        all_v = [(c.get("nom",""),v) for c in chantiers for v in c.get("visites",[])]
        all_v.sort(key=lambda x: x[1].get("date",""), reverse=True)
        if not all_v:
            st.info("Aucune visite enregistrée.")
        for nom_c,v in all_v[:8]:
            nb_i = len(v.get("images",[]))
            st.markdown(f"""
            <div class="card" style="padding:10px 16px;margin-bottom:6px">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                    <span style="font-weight:600">📅 {v.get('date','—')}</span>
                    <span style="color:#7a9bbf;font-size:13px">{nom_c[:38]}</span>
                    {b_etat(v.get('etat','—'))}
                    <span style="color:#7a9bbf;font-size:12px">👷 {v.get('inspecteur','—')}</span>
                    {"<span style='color:#0096ff;font-size:12px;margin-left:auto'>🖼 "+str(nb_i)+"</span>" if nb_i else ""}
                </div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE CHANTIERS
# ═══════════════════════════════════════════════════════════════════════

def page_chantiers():
    bandeau()
    data      = get_data()
    chantiers = data.get("chantiers",[])

    # ── Mode formulaire création/édition ────────────────────────────────
    mode = st.session_state.get("page_mode","liste")

    if mode == "nouveau_chantier":
        form_chantier(edit_c=None)
        return

    if mode == "edit_chantier":
        cid    = st.session_state.get("chantier_edit_id")
        edit_c = next((c for c in chantiers if c["id"]==cid), None)
        if edit_c:
            form_chantier(edit_c=edit_c)
        else:
            st.error("Chantier introuvable.")
            st.session_state.page_mode = "liste"
            st.rerun()
        return

    if mode == "confirm_del":
        cid = st.session_state.get("chantier_edit_id")
        ch  = next((c for c in chantiers if c["id"]==cid), None)
        if ch:
            st.warning(f"⚠️ Supprimer définitivement **{ch['nom']}** et toutes ses visites ?")
            col_y, col_n = st.columns(2)
            if col_y.button("✔ Oui, supprimer", type="primary", use_container_width=True):
                data["chantiers"] = [c for c in chantiers if c["id"]!=cid]
                sauvegarder(data)
                st.session_state.data      = data
                st.session_state.page_mode = "liste"
                st.success("Chantier supprimé.")
                st.rerun()
            if col_n.button("✖ Annuler", use_container_width=True):
                st.session_state.page_mode = "liste"
                st.rerun()
        return

    # ── Mode liste ───────────────────────────────────────────────────────
    st.title("🏗 Chantiers")
    col_s, col_b = st.columns([3,1])
    with col_s:
        rech = st.text_input("🔍", placeholder="Rechercher par nom, localisation, entreprise…",
                             label_visibility="collapsed")
    with col_b:
        if est_admin():
            if st.button("➕ Nouveau chantier", use_container_width=True, type="primary"):
                st.session_state.page_mode = "nouveau_chantier"
                st.rerun()

    st.markdown("---")

    filtres = [c for c in chantiers if
               rech.lower() in c.get("nom","").lower() or
               rech.lower() in c.get("localisation","").lower() or
               rech.lower() in c.get("entreprise","").lower()] if rech else chantiers

    if not filtres:
        st.info("Aucun chantier trouvé.")
        return

    for c in filtres:
        nb_v = len(c.get("visites",[]))
        nb_i = sum(len(v.get("images",[])) for v in c.get("visites",[]))
        st.markdown(f"""
        <div class="card">
            <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px">
                <span style="font-size:1.1em;font-weight:700">{c.get('nom','—')}</span>
                {b_statut(c.get('statut','—'))}
            </div>
            <div class="info-row">
                <div class="info-item"><label>📍 Localisation</label>
                    <span>{c.get('localisation','—')}</span></div>
                <div class="info-item"><label>🏢 Entreprise</label>
                    <span>{c.get('entreprise','—') or '—'}</span></div>
                <div class="info-item"><label>👷 Responsable</label>
                    <span>{c.get('responsable','—') or '—'}</span></div>
                <div class="info-item"><label>📅 Début</label>
                    <span>{c.get('date_debut','—') or '—'}</span></div>
                <div class="info-item"><label>🔍 Visites</label>
                    <span style="color:#0096ff;font-weight:600">{nb_v}</span></div>
                <div class="info-item"><label>🖼 Images</label>
                    <span style="color:#ffb347;font-weight:600">{nb_i}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

        if est_admin():
            b1,b2,b3 = st.columns([3,1,1])
            with b1:
                if st.button(f"📂 Ouvrir — {c['nom'][:30]}", key=f"op_{c['id']}",
                             use_container_width=True):
                    st.session_state.chantier_actif = c["id"]
                    st.session_state.page = "detail"
                    st.session_state.visite_mode = "liste"
                    st.rerun()
            with b2:
                if st.button("✏ Modifier", key=f"ed_{c['id']}", use_container_width=True):
                    st.session_state.page_mode       = "edit_chantier"
                    st.session_state.chantier_edit_id = c["id"]
                    st.rerun()
            with b3:
                if st.button("🗑 Suppr.", key=f"dl_{c['id']}", use_container_width=True):
                    st.session_state.page_mode        = "confirm_del"
                    st.session_state.chantier_edit_id = c["id"]
                    st.rerun()
        else:
            if st.button(f"📂 Voir le détail", key=f"op_{c['id']}"):
                st.session_state.chantier_actif = c["id"]
                st.session_state.page           = "detail"
                st.session_state.visite_mode    = "liste"
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# PAGE DÉTAIL CHANTIER
# ═══════════════════════════════════════════════════════════════════════

def page_detail():
    bandeau()
    data     = get_data()
    cid      = st.session_state.get("chantier_actif")
    chantier = next((c for c in data.get("chantiers",[]) if c["id"]==cid), None)

    if not chantier:
        st.error("Chantier introuvable.")
        if st.button("← Retour"):
            st.session_state.page = "chantiers"
            st.rerun()
        return

    # ── Navigation retour ────────────────────────────────────────────────
    if st.button("← Retour à la liste"):
        st.session_state.page        = "chantiers"
        st.session_state.page_mode   = "liste"
        st.session_state.visite_mode = "liste"
        st.rerun()

    # ── En-tête ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <h1 style="margin-top:0">{chantier.get('nom','—')}
    <span style="margin-left:12px">{b_statut(chantier.get('statut','—'))}</span></h1>""",
    unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-row">
        <div class="info-item"><label>📍 Localisation</label>
            <span>{chantier.get('localisation','—')}</span></div>
        <div class="info-item"><label>🏢 Entreprise</label>
            <span>{chantier.get('entreprise','—') or '—'}</span></div>
        <div class="info-item"><label>👷 Responsable</label>
            <span>{chantier.get('responsable','—') or '—'}</span></div>
        <div class="info-item"><label>🔧 Travaux</label>
            <span>{chantier.get('type_travaux','—') or '—'}</span></div>
        <div class="info-item"><label>📅 Début</label>
            <span>{chantier.get('date_debut','—') or '—'}</span></div>
        <div class="info-item"><label>🏁 Fin prévue</label>
            <span>{chantier.get('date_fin','—') or '—'}</span></div>
    </div>""", unsafe_allow_html=True)

    if chantier.get("observations"):
        st.info(f"📝 {chantier['observations']}")

    if est_admin():
        ca,cb = st.columns(2)
        if ca.button("✏ Modifier ce chantier", use_container_width=True):
            st.session_state.page_mode        = "edit_chantier"
            st.session_state.chantier_edit_id = chantier["id"]
            st.session_state.page             = "chantiers"
            st.rerun()
        if cb.button("🗑 Supprimer ce chantier", use_container_width=True):
            st.session_state.page_mode        = "confirm_del"
            st.session_state.chantier_edit_id = chantier["id"]
            st.session_state.page             = "chantiers"
            st.rerun()

    st.markdown("---")

    # ── Onglets ──────────────────────────────────────────────────────────
    tab_v, tab_i = st.tabs(["🔍 Visites d'inspection", "🖼 Bibliothèque d'images"])

    # ════════ ONGLET VISITES ══════════════════════════════════════════════
    with tab_v:
        vmode = st.session_state.get("visite_mode","liste")

        # Formulaire nouvelle visite
        if vmode == "nouvelle_visite":
            form_visite(chantier, edit_v=None)
            return

        # Formulaire modification visite
        if vmode == "edit_visite":
            vid    = st.session_state.get("visite_edit_id")
            edit_v = next((v for v in chantier.get("visites",[]) if v["id"]==vid), None)
            if edit_v:
                form_visite(chantier, edit_v=edit_v)
            else:
                st.error("Visite introuvable.")
                st.session_state.visite_mode = "liste"
                st.rerun()
            return

        # Confirmation suppression visite
        if vmode == "confirm_del_visite":
            vid = st.session_state.get("visite_edit_id")
            v   = next((v for v in chantier.get("visites",[]) if v["id"]==vid), None)
            if v:
                st.warning(f"⚠️ Supprimer la visite du **{v.get('date','—')}** ?")
                cy,cn = st.columns(2)
                if cy.button("✔ Oui, supprimer", type="primary", use_container_width=True):
                    chantier["visites"] = [x for x in chantier["visites"] if x["id"]!=vid]
                    sauvegarder(data)
                    st.session_state.data        = data
                    st.session_state.visite_mode = "liste"
                    st.success("Visite supprimée.")
                    st.rerun()
                if cn.button("✖ Annuler", use_container_width=True):
                    st.session_state.visite_mode = "liste"
                    st.rerun()
            return

        # ── Liste visites ─────────────────────────────────────────────────
        if est_admin():
            if st.button("➕ Nouvelle visite", type="primary"):
                st.session_state.visite_mode = "nouvelle_visite"
                st.rerun()

        visites = sorted(chantier.get("visites",[]),
                         key=lambda v: v.get("date",""), reverse=True)
        if not visites:
            st.info("Aucune visite." + (" Ajoutez-en une ci-dessus." if est_admin() else ""))
        else:
            for v in visites:
                nb_i = len(v.get("images",[]))
                obs  = v.get("observations","")
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                        <span style="font-weight:700;font-size:1.05em">📅 {v.get('date','—')}</span>
                        {b_etat(v.get('etat','—'))}
                        <span style="color:#7a9bbf;font-size:13px">⭐ {v.get('note','—')}/10</span>
                        <span style="color:#7a9bbf;font-size:13px">👷 {v.get('inspecteur','—')}</span>
                        <span style="color:{'#0096ff' if nb_i else '#445566'};
                               font-size:13px;margin-left:auto">🖼 {nb_i} image(s)</span>
                    </div>
                    {"<p style='margin:8px 0 0;color:#7a9bbf;font-size:13px'>" + obs[:160] + ("…" if len(obs)>160 else "")+"</p>" if obs else ""}
                </div>""", unsafe_allow_html=True)

                if est_admin():
                    bv1,bv2,bv3 = st.columns([3,1,1])
                    with bv1:
                        if st.button(f"🖼 Images ({nb_i})",
                                     key=f"imgs_{v['id']}", use_container_width=True):
                            st.session_state.visite_images = v["id"]
                            st.rerun()
                    with bv2:
                        if st.button("✏", key=f"ev_{v['id']}", use_container_width=True):
                            st.session_state.visite_mode    = "edit_visite"
                            st.session_state.visite_edit_id = v["id"]
                            st.rerun()
                    with bv3:
                        if st.button("🗑", key=f"dv_{v['id']}", use_container_width=True):
                            st.session_state.visite_mode    = "confirm_del_visite"
                            st.session_state.visite_edit_id = v["id"]
                            st.rerun()
                else:
                    if st.button(f"🖼 Voir images ({nb_i})", key=f"imgs_{v['id']}"):
                        st.session_state.visite_images = v["id"]
                        st.rerun()

    # ════════ ONGLET IMAGES ═══════════════════════════════════════════════
    with tab_i:
        visites = chantier.get("visites",[])
        if not visites:
            st.info("Créez d'abord une visite pour y ajouter des images.")
        else:
            options = {f"📅 {v.get('date','—')} — {v.get('inspecteur','—')}": v["id"]
                       for v in sorted(visites, key=lambda x: x.get("date",""), reverse=True)}
            dv  = st.session_state.get("visite_images")
            dk  = next((k for k,val in options.items() if val==dv),
                       list(options.keys())[0]) if dv else list(options.keys())[0]
            sel = st.selectbox("Sélectionner une visite", list(options.keys()),
                               index=list(options.keys()).index(dk))
            vid    = options[sel]
            visite = next(v for v in visites if v["id"]==vid)

            st.markdown(f"""
            <div class="info-row">
                <div class="info-item"><label>📅 Date</label>
                    <span>{visite.get('date','—')}</span></div>
                <div class="info-item"><label>👷 Inspecteur</label>
                    <span>{visite.get('inspecteur','—')}</span></div>
                <div class="info-item"><label>État</label>
                    <span>{b_etat(visite.get('etat','—'))}</span></div>
                <div class="info-item"><label>🖼 Images</label>
                    <span style="color:#ffb347;font-weight:700">
                    {len(visite.get('images',[]))}</span></div>
            </div>""", unsafe_allow_html=True)

            if est_admin():
                with st.expander("➕ Ajouter des images", expanded=False):
                    uploaded = st.file_uploader(
                        "Choisir des photos",
                        type=["jpg","jpeg","png","bmp","gif","webp","tiff"],
                        accept_multiple_files=True, key=f"up_{vid}")
                    if st.button("📤 Enregistrer les images", type="primary") and uploaded:
                        dossier = IMG_DIR/vid; dossier.mkdir(parents=True, exist_ok=True)
                        ajouts = []
                        for f in uploaded:
                            dest = dossier/f.name
                            stem,ext = os.path.splitext(f.name); k=1
                            while dest.exists():
                                dest=dossier/f"{stem}_{k}{ext}"; k+=1
                            with open(dest,"wb") as out: out.write(f.read())
                            ajouts.append(f"images/{vid}/{dest.name}")
                        visite.setdefault("images",[]).extend(ajouts)
                        sauvegarder(data)
                        st.session_state.data = data
                        st.success(f"{len(ajouts)} image(s) ajoutée(s) ✓")
                        st.rerun()

            imgs = visite.get("images",[])
            if not imgs:
                msg = "Aucune image pour cette visite."
                st.info(msg + (" Ajoutez-en ci-dessus." if est_admin() else ""))
            else:
                st.markdown(f"**{len(imgs)} image(s)**")
                cols = st.columns(4)
                for idx,chemin in enumerate(imgs):
                    path = BASE_DIR/chemin
                    with cols[idx%4]:
                        if path.exists():
                            st.image(str(path), use_container_width=True,
                                     caption=Path(chemin).name)
                            if est_admin():
                                if st.button("🗑", key=f"di_{vid}_{idx}",
                                             use_container_width=True):
                                    visite["images"].pop(idx)
                                    sauvegarder(data)
                                    st.session_state.data = data
                                    st.rerun()
                        else:
                            st.markdown("<span style='color:#ff4d6d'>❌ Introuvable</span>",
                                        unsafe_allow_html=True)
                if est_admin():
                    st.markdown("---")
                    if st.button("🗑 Vider toute la galerie", type="secondary"):
                        visite["images"] = []
                        sauvegarder(data)
                        st.session_state.data = data
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════

def sidebar():
    data = get_data()
    ch   = data.get("chantiers",[])
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 8px">
            <div style="font-size:2.2em;font-weight:800;color:#00c8aa;letter-spacing:1px">DIAT</div>
            <div style="font-size:11px;color:#7a9bbf;margin-top:2px">
                Diagnostic & Inspection<br>Audit de Terrain</div>
        </div>
        <hr style="border-color:#2a3f58;margin:8px 0 12px">
        """, unsafe_allow_html=True)

        # Badge rôle
        if est_admin():
            st.markdown('<span class="badge badge-encours">🔑 Mode Admin</span>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge badge-nondmarre">👁 Lecture seule</span>',
                        unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation
        page = st.session_state.get("page","dashboard")
        if st.button("📊 Tableau de bord", use_container_width=True,
                     type="primary" if page=="dashboard" else "secondary"):
            st.session_state.page = "dashboard"; st.rerun()
        if st.button("🏗 Chantiers", use_container_width=True,
                     type="primary" if page=="chantiers" else "secondary"):
            st.session_state.page      = "chantiers"
            st.session_state.page_mode = "liste"
            st.rerun()

        st.markdown("---")
        st.caption("CHANTIERS")

        for c in ch:
            ico = ("🟢" if c.get("statut")=="En cours"
                   else "✅" if c.get("statut")=="Terminé"
                   else "⏸")
            if st.button(f"{ico} {c.get('nom','—')[:28]}",
                         key=f"sb_{c['id']}", use_container_width=True):
                st.session_state.chantier_actif = c["id"]
                st.session_state.page           = "detail"
                st.session_state.visite_mode    = "liste"
                st.rerun()

        st.markdown("---")
        tv = sum(len(c.get("visites",[])) for c in ch)
        ti = sum(len(v.get("images",[])) for c in ch for v in c.get("visites",[]))
        st.markdown(f"""
        <div style="padding:10px;background:#172030;border-radius:8px;
                    border:1px solid #2a3f58;font-size:12px;color:#7a9bbf">
            🏗 {len(ch)} chantier(s)<br>
            🔍 {tv} visite(s)<br>
            🖼 {ti} image(s)
        </div>""", unsafe_allow_html=True)

        # Connexion admin
        st.markdown("---")
        with st.expander("🔒 Connexion admin", expanded=False):
            if est_admin():
                st.success("Connecté en mode admin")
                if st.button("🔓 Se déconnecter", use_container_width=True):
                    st.session_state.admin = False; st.rerun()
            else:
                pwd = st.text_input("Mot de passe", type="password", key="pwd_in")
                if st.button("🔑 Connexion", use_container_width=True, type="primary"):
                    if check_mdp(pwd):
                        st.session_state.admin = True
                        st.success("Connecté ✓"); st.rerun()
                    else:
                        st.error("Mot de passe incorrect")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    for key,val in [("page","dashboard"),("page_mode","liste"),
                    ("visite_mode","liste"),("admin",False),("modal",None)]:
        if key not in st.session_state:
            st.session_state[key] = val

    sidebar()

    page = st.session_state.get("page","dashboard")
    if   page == "dashboard": page_dashboard()
    elif page == "chantiers": page_chantiers()
    elif page == "detail":    page_detail()
    else:                     page_dashboard()

if __name__ == "__main__":
    main()
