"""
MedNavigator — Streamlit App
Shoppers Drug Mart #1221 · Brooklin, ON
"""

import streamlit as st
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
DATA_FILE  = Path(__file__).parent / "medications.json"
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

CATEGORIES = [
    "All", "BP & Heart", "Cholesterol", "Diabetes", "Blood Thinner",
    "Mental Health", "Pain & Nerve", "Sleep & Anxiety", "Antibiotics",
    "Stomach", "Thyroid & Hormones", "Bladder & Prostate", "Opioid", "Other",
]

CAT_ICONS = {
    "All":"💊","BP & Heart":"❤️","Cholesterol":"🩸","Diabetes":"💉",
    "Blood Thinner":"🩹","Mental Health":"🧠","Pain & Nerve":"⚡",
    "Sleep & Anxiety":"😴","Antibiotics":"🦠","Stomach":"🫁",
    "Thyroid & Hormones":"🌸","Bladder & Prostate":"💧","Opioid":"⚠️","Other":"🔬",
}

ODB_COLORS = {
    "Covered":     ("#15803d", "#dcfce7"),
    "Limited Use": ("#b45309", "#fef3c7"),
    "Not Covered": ("#b91c1c", "#fee2e2"),
}

# ── Data helpers ─────────────────────────────────────────────────────────────
def load_drugs() -> list[dict]:
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_drugs(drugs: list[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(drugs, f, indent=2, ensure_ascii=False)

# ── OpenAI enrichment ─────────────────────────────────────────────────────────
def enrich_drug(name: str, strength: str, din: str) -> dict:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        prompt = f"""You are a Canadian pharmacy expert. Return ONLY valid JSON for this drug:
Drug: {name}
Strength: {strength}
DIN: {din}

Return this exact JSON structure (no markdown, no explanation):
{{
  "commonName": "lay-person name e.g. 'Blood Pressure Pill (Norvasc type)'",
  "category": "one of: BP & Heart | Cholesterol | Diabetes | Blood Thinner | Mental Health | Pain & Nerve | Sleep & Anxiety | Antibiotics | Stomach | Thyroid & Hormones | Bladder & Prostate | Opioid | Other",
  "drugClass": "e.g. Calcium Channel Blocker",
  "condition": "primary conditions separated by ' / '",
  "brands": ["Brand1", "Brand2"],
  "isGeneric": true or false,
  "odb": "Covered | Limited Use | Not Covered",
  "odbNotes": "one sentence about Ontario ODB coverage, LU code if needed",
  "copay": true or false,
  "copayInfo": "manufacturer name, phone number, website if copay=true, else empty string",
  "controlled": true or false,
  "opioid": true or false,
  "pillShape": "tablet | capsule | oval | gel",
  "c1": "#hexcolor matching typical pill color",
  "c2": "#hexcolor for second half if capsule, else same as c1"
}}"""
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=600,
        )
        raw = resp.choices[0].message.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        st.warning(f"OpenAI enrichment failed: {e}. Fill fields manually.")
        return {}

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #f1f5f9; }
[data-testid="stSidebar"] { background: white; border-right: 1px solid #e2e8f0; }
[data-testid="stSidebar"] h2 { font-size: 14px; font-weight: 700; color: #1e5fa8; margin-bottom: 4px; }

/* ── Header banner ── */
.med-header {
  background: linear-gradient(135deg,#1e5fa8,#153f70);
  border-radius: 12px; padding: 18px 24px; color: white;
  display: flex; align-items: center; gap: 14px; margin-bottom: 16px;
}
.med-header h1 { font-size: 22px; margin: 0; }
.med-header p  { font-size: 12px; opacity: .75; margin: 2px 0 0; }

/* ── Category pills ── */
.cat-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.cat-btn {
  padding: 6px 13px; border-radius: 20px; font-size: 12px; font-weight: 600;
  border: 1.5px solid #e2e8f0; background: white; cursor: pointer;
  color: #475569; transition: all .15s; white-space: nowrap;
}
.cat-btn.active { background: #1e5fa8; color: white; border-color: #1e5fa8; }

/* ── Drug card ── */
.drug-card {
  background: white; border-radius: 12px; border: 1px solid #e2e8f0;
  padding: 0; overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,.07);
  transition: box-shadow .15s;
}
.drug-card:hover { box-shadow: 0 4px 18px rgba(0,0,0,.12); }

.card-top {
  padding: 13px 14px 9px; display: flex; gap: 11px;
  border-bottom: 1px solid #f8fafc; align-items: flex-start;
}
.pill-circle {
  width: 42px; height: 21px; border-radius: 10px; flex-shrink: 0; margin-top: 3px;
  box-shadow: inset 0 -2px 3px rgba(0,0,0,.18);
}
.pill-circle.tablet { border-radius: 5px; }
.pill-circle.gel    { width:28px;height:28px;border-radius:50%;margin-top:0; }

.drug-name   { font-size: 15px; font-weight: 700; color: #0f172a; line-height: 1.2; }
.drug-str    { font-size: 12px; color: #64748b; margin-top: 1px; }
.common-name {
  display:inline-block; margin-top:5px;
  background:#fef3c7;color:#92400e;border:1px solid #fde68a;
  border-radius:4px;font-size:10px;font-weight:700;padding:2px 7px;
}

.card-body { padding: 10px 14px; }
.info-row  { display:flex;gap:6px;align-items:flex-start;margin-bottom:5px;font-size:13px; }
.lbl  { font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#94a3b8;min-width:62px;padding-top:2px;flex-shrink:0; }
.val  { color:#334155;flex:1;line-height:1.4; }
.cls-chip { background:#e0f2fe;color:#0369a1;border-radius:4px;font-size:11px;font-weight:600;padding:2px 7px;display:inline-block; }
.brand-tag { background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0;border-radius:4px;font-size:11px;padding:1px 6px;margin:1px 2px 1px 0;display:inline-block; }

.card-foot { padding:8px 14px 12px;display:flex;flex-wrap:wrap;gap:5px;border-top:1px solid #f1f5f9; }
.badge { display:inline-flex;align-items:center;gap:3px;padding:3px 9px;border-radius:20px;font-size:11px;font-weight:700; }
.b-cov   { background:#dcfce7;color:#15803d; }
.b-lim   { background:#fef3c7;color:#b45309; }
.b-not   { background:#fee2e2;color:#b91c1c; }
.b-gen   { background:#f0f9ff;color:#0369a1; }
.b-brand { background:#faf5ff;color:#7c3aed; }
.b-ctrl  { background:#fff7ed;color:#b45309; }
.b-opioid{ background:#fff7ed;color:#c2410c; }
.b-tri   { background:#f0fdf4;color:#15803d; }
.b-copay { background:#f5f3ff;color:#7c3aed; }

/* ── Copay steps box ── */
.copay-box { background:#faf5ff;border:1px solid #e9d5ff;border-radius:10px;padding:14px;margin-top:8px; }
.copay-box h4 { color:#7c3aed;font-size:13px;margin-bottom:10px; }
.step-row { display:flex;gap:10px;margin-bottom:10px;align-items:flex-start; }
.step-num { width:24px;height:24px;border-radius:50%;background:#7c3aed;color:white;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px; }
.step-content strong { display:block;font-size:12px;color:#1e293b;margin-bottom:1px; }
.step-content span   { font-size:11px;color:#64748b;line-height:1.5; }
.copay-ref { background:#ede9fe;border-radius:6px;padding:8px 10px;font-size:11px;color:#5b21b6;margin-top:6px; }

/* ── Add form ── */
.form-section { background:white;border-radius:12px;border:1px solid #e2e8f0;padding:20px;margin-bottom:14px; }
.form-section h3 { font-size:14px;font-weight:700;color:#1e5fa8;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #e2e8f0; }

/* ── Stats strip ── */
.stat-strip { display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap; }
.stat-box { background:white;border-radius:10px;border:1px solid #e2e8f0;padding:12px 16px;text-align:center;flex:1;min-width:100px; }
.stat-box .num { font-size:22px;font-weight:800;color:#1e5fa8; }
.stat-box .lbl { font-size:11px;color:#64748b;margin-top:1px; }
</style>
""", unsafe_allow_html=True)

# ── Card renderer ─────────────────────────────────────────────────────────────
def render_card(drug: dict, show_copay_steps: bool = False) -> str:
    odb = drug.get("odb", "Not Covered")
    fg, bg = ODB_COLORS.get(odb, ("#64748b", "#f1f5f9"))
    odb_icon = "🟢" if odb == "Covered" else "🟡" if odb == "Limited Use" else "🔴"

    c1   = drug.get("c1", "#94a3b8")
    c2   = drug.get("c2", c1)
    shape = drug.get("pillShape", "oval")

    if shape == "capsule":
        pill_style = f"background:linear-gradient(90deg,{c1} 50%,{c2} 50%)"
    else:
        pill_style = f"background:{c1}"

    brands_html = "".join(f'<span class="brand-tag">{b}</span>' for b in drug.get("brands", []))

    badges = [f'<span class="badge b-cov">{odb_icon} {odb}</span>' if odb == "Covered"
              else f'<span class="badge b-lim">{odb_icon} {odb}</span>' if odb == "Limited Use"
              else f'<span class="badge b-not">{odb_icon} {odb}</span>']

    if drug.get("isGeneric"):
        badges.append('<span class="badge b-gen">Ⓖ Generic</span>')
    else:
        badges.append('<span class="badge b-brand">® Brand</span>')

    if drug.get("copay"):
        badges.append('<span class="badge b-copay">⭐ Copay Card</span>')
    if drug.get("opioid"):
        badges.append('<span class="badge b-opioid">⚠ Opioid</span>')
    elif drug.get("controlled"):
        badges.append('<span class="badge b-ctrl">🔒 Controlled</span>')
    if odb != "Not Covered" and not drug.get("opioid") and not drug.get("controlled"):
        badges.append('<span class="badge b-tri">🍁 Trillium</span>')

    din_str = f" · DIN {drug['din']}" if drug.get("din") else ""

    # Copay steps section
    copay_html = ""
    if show_copay_steps and drug.get("copay") and drug.get("copaySteps"):
        s = drug["copaySteps"]
        steps_html = "".join(f"""
        <div class="step-row">
          <div class="step-num">{i+1}</div>
          <div class="step-content">
            <strong>{st_["title"]}</strong>
            <span>{st_["detail"]}</span>
          </div>
        </div>""" for i, st_ in enumerate(s.get("steps", [])))
        copay_html = f"""
        <div class="copay-box">
          <h4>⭐ How to Access the {s.get('name','')} Copay Card</h4>
          {steps_html}
          <div class="copay-ref">📞 {s.get('manufacturer','')} &nbsp;·&nbsp; <strong>{s.get('phone','')}</strong> &nbsp;·&nbsp; {s.get('website','')}</div>
        </div>"""

    return f"""
<div class="drug-card">
  <div class="card-top">
    <div class="pill-circle {shape}" style="{pill_style}"></div>
    <div>
      <div class="drug-name">{drug['name']}</div>
      <div class="drug-str">{drug.get('strength','')}{din_str}</div>
      <div class="common-name">{drug.get('commonName','')}</div>
    </div>
  </div>
  <div class="card-body">
    <div class="info-row"><span class="lbl">Treats</span><span class="val">{drug.get('condition','')}</span></div>
    <div class="info-row"><span class="lbl">Class</span><span class="val"><span class="cls-chip">{drug.get('drugClass','')}</span></span></div>
    <div class="info-row"><span class="lbl">Brands</span><span class="val">{brands_html}</span></div>
    <div class="info-row"><span class="lbl">ODB</span><span class="val" style="font-size:12px;color:#475569">{drug.get('odbNotes','')}</span></div>
    {copay_html}
  </div>
  <div class="card-foot">{''.join(badges)}</div>
</div>"""

# ── Sidebar filters ──────────────────────────────────────────────────────────
def sidebar_filters(drugs: list[dict]):
    with st.sidebar:
        st.markdown("## 🔍 Search")
        q = st.text_input("", placeholder="Drug name, brand, condition…", label_visibility="collapsed")

        st.markdown("## 📂 Category")
        selected_cat = st.radio(
            "",
            options=CATEGORIES,
            format_func=lambda c: f"{CAT_ICONS.get(c,'')} {c}",
            label_visibility="collapsed",
        )

        st.markdown("## 💊 ODB Status")
        odb_filter = st.radio("", ["All", "Covered", "Limited Use", "Not Covered"],
                              label_visibility="collapsed")

        st.markdown("## ⭐ Extras")
        copay_only   = st.checkbox("Has copay / patient assist card")
        generic_only = st.checkbox("Generic only")
        show_copay_steps = st.checkbox("Show copay steps on card", value=False)

        st.markdown("---")
        st.caption("Tony Huynh Drugs Ltd · Shoppers #1221")

    return q, selected_cat, odb_filter, copay_only, generic_only, show_copay_steps

# ── Dashboard tab ─────────────────────────────────────────────────────────────
def tab_dashboard(drugs: list[dict]):
    q, selected_cat, odb_filter, copay_only, generic_only, show_copay_steps = sidebar_filters(drugs)

    # Filter
    filtered = drugs
    if q:
        ql = q.lower()
        filtered = [d for d in filtered if
            ql in d.get("name","").lower() or
            ql in d.get("commonName","").lower() or
            ql in d.get("condition","").lower() or
            ql in d.get("drugClass","").lower() or
            any(ql in b.lower() for b in d.get("brands",[]))]
    if selected_cat != "All":
        filtered = [d for d in filtered if d.get("category") == selected_cat]
    if odb_filter != "All":
        filtered = [d for d in filtered if d.get("odb") == odb_filter]
    if copay_only:
        filtered = [d for d in filtered if d.get("copay")]
    if generic_only:
        filtered = [d for d in filtered if d.get("isGeneric")]

    # Stats strip
    n_cov  = sum(1 for d in filtered if d.get("odb") == "Covered")
    n_lim  = sum(1 for d in filtered if d.get("odb") == "Limited Use")
    n_not  = sum(1 for d in filtered if d.get("odb") == "Not Covered")
    n_cop  = sum(1 for d in filtered if d.get("copay"))

    st.markdown(f"""
<div class="stat-strip">
  <div class="stat-box"><div class="num">{len(filtered)}</div><div class="lbl">Medications</div></div>
  <div class="stat-box"><div class="num" style="color:#15803d">{n_cov}</div><div class="lbl">🟢 ODB Covered</div></div>
  <div class="stat-box"><div class="num" style="color:#b45309">{n_lim}</div><div class="lbl">🟡 Limited Use</div></div>
  <div class="stat-box"><div class="num" style="color:#b91c1c">{n_not}</div><div class="lbl">🔴 Not Covered</div></div>
  <div class="stat-box"><div class="num" style="color:#7c3aed">{n_cop}</div><div class="lbl">⭐ Copay Cards</div></div>
</div>""", unsafe_allow_html=True)

    if not filtered:
        st.info("No medications match your filters. Try clearing some.")
        return

    # Card grid — 3 columns
    cols = st.columns(3, gap="medium")
    for i, drug in enumerate(filtered):
        with cols[i % 3]:
            st.markdown(render_card(drug, show_copay_steps), unsafe_allow_html=True)
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Add / Edit tab ────────────────────────────────────────────────────────────
def tab_add_edit(drugs: list[dict]):
    st.markdown("### ➕ Add or Edit a Medication")
    st.caption("Type a drug name and optionally a DIN, then click **Auto-fill with AI** to have OpenAI populate the fields. Review and save when ready.")

    # ── Auto-fill section ──
    st.markdown('<div class="form-section"><h3>🤖 AI Auto-Fill</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    drug_name_ai = c1.text_input("Drug Name", placeholder="e.g. LISINOPRIL", key="ai_name")
    strength_ai  = c2.text_input("Strength",  placeholder="e.g. 10 MG",      key="ai_str")
    din_ai       = c3.text_input("DIN",        placeholder="8-digit DIN",     key="ai_din")

    if "ai_data" not in st.session_state:
        st.session_state.ai_data = {}

    col_btn, col_msg = st.columns([1, 3])
    if col_btn.button("✨ Auto-fill with AI", use_container_width=True):
        if not drug_name_ai.strip():
            col_msg.warning("Enter a drug name first.")
        elif not OPENAI_KEY:
            col_msg.error("No OPENAI_API_KEY found — add it to your .env file.")
        else:
            with st.spinner("Asking OpenAI…"):
                data = enrich_drug(drug_name_ai.strip().upper(), strength_ai.strip(), din_ai.strip())
            if data:
                st.session_state.ai_data = data
                col_msg.success("✅ Fields populated — review below and save.")
    st.markdown("</div>", unsafe_allow_html=True)

    ai = st.session_state.ai_data

    # ── Edit / select existing ──
    st.markdown('<div class="form-section"><h3>📝 Edit Existing Medication</h3>', unsafe_allow_html=True)
    existing_labels = ["— Add New —"] + [f"{d['name']} {d.get('strength','')}" for d in drugs]
    chosen = st.selectbox("Select to edit an existing entry", existing_labels)
    existing = None
    if chosen != "— Add New —":
        idx = existing_labels.index(chosen) - 1
        existing = drugs[idx]
    st.markdown("</div>", unsafe_allow_html=True)

    src = existing or {}

    # ── Full form ──
    st.markdown('<div class="form-section"><h3>📋 Medication Details</h3>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    name     = r1c1.text_input("Drug Name *",  value=src.get("name", drug_name_ai.upper() if drug_name_ai else ""))
    strength = r1c2.text_input("Strength *",   value=src.get("strength", ai.get("strength", strength_ai)))
    din      = r1c3.text_input("DIN",          value=src.get("din",      ai.get("din", din_ai)))

    r2c1, r2c2, r2c3 = st.columns(3)
    mfr       = r2c1.text_input("Manufacturer Code", value=src.get("mfr", ""))
    common    = r2c2.text_input("Common Name (lay term) *",
                                value=src.get("commonName", ai.get("commonName", "")),
                                help="e.g. 'Blood Pressure Pill (Norvasc type)'")
    category  = r2c3.selectbox("Category *",
                                [c for c in CATEGORIES if c != "All"],
                                index=max(0, [c for c in CATEGORIES if c != "All"].index(
                                    src.get("category", ai.get("category", "Other"))
                                ) if src.get("category", ai.get("category", "Other")) in CATEGORIES else 0))

    drug_class = st.text_input("Drug Class *",
                               value=src.get("drugClass", ai.get("drugClass", "")),
                               help="e.g. Calcium Channel Blocker, Statin, SSRI")
    condition  = st.text_input("Treats / Condition *",
                               value=src.get("condition", ai.get("condition", "")),
                               help="Separate multiple with ' / '")
    brands_raw = st.text_input("Brand Name(s)",
                               value=", ".join(src.get("brands", ai.get("brands", []))),
                               help="Comma-separated, e.g. Lipitor, Atorvastatin")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── ODB + flags ──
    st.markdown('<div class="form-section"><h3>🏥 Ontario ODB & Coverage</h3>', unsafe_allow_html=True)

    od1, od2 = st.columns([1, 2])
    odb_status = od1.selectbox("ODB Status *",
                               ["Covered", "Limited Use", "Not Covered"],
                               index=["Covered","Limited Use","Not Covered"].index(
                                   src.get("odb", ai.get("odb", "Covered"))))
    odb_notes  = od2.text_input("ODB Notes",
                                value=src.get("odbNotes", ai.get("odbNotes", "")))

    fl1, fl2, fl3, fl4 = st.columns(4)
    is_generic = fl1.checkbox("Generic",    value=src.get("isGeneric", ai.get("isGeneric", True)))
    controlled = fl2.checkbox("Controlled", value=src.get("controlled", ai.get("controlled", False)))
    opioid     = fl3.checkbox("Opioid",     value=src.get("opioid",     ai.get("opioid", False)))
    has_copay  = fl4.checkbox("Has Copay Card", value=src.get("copay",  ai.get("copay", False)))

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Copay Card Details ──
    copay_steps_data = src.get("copaySteps") or {}
    if has_copay:
        st.markdown('<div class="form-section"><h3>⭐ Copay / Patient Assistance Card Details</h3>', unsafe_allow_html=True)
        cp1, cp2, cp3 = st.columns(3)
        cp_mfr     = cp1.text_input("Manufacturer",  value=copay_steps_data.get("manufacturer",""))
        cp_phone   = cp2.text_input("Phone Number",   value=copay_steps_data.get("phone",""))
        cp_website = cp3.text_input("Website",        value=copay_steps_data.get("website",""))

        st.markdown("**Step-by-step instructions** (up to 5 steps):")
        existing_steps = copay_steps_data.get("steps", [])
        steps_out = []
        for i in range(5):
            sc1, sc2 = st.columns([1, 2])
            s_title  = sc1.text_input(f"Step {i+1} Title",  value=existing_steps[i]["title"]  if i < len(existing_steps) else "", key=f"st{i}")
            s_detail = sc2.text_input(f"Step {i+1} Detail", value=existing_steps[i]["detail"] if i < len(existing_steps) else "", key=f"sd{i}")
            if s_title.strip():
                steps_out.append({"title": s_title.strip(), "detail": s_detail.strip()})
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        cp_mfr = cp_phone = cp_website = ""
        steps_out = []

    # ── Pill visuals ──
    st.markdown('<div class="form-section"><h3>💊 Visual (optional)</h3>', unsafe_allow_html=True)
    pv1, pv2, pv3 = st.columns(3)
    pill_shape = pv1.selectbox("Pill Shape",
                               ["oval","tablet","capsule","gel"],
                               index=["oval","tablet","capsule","gel"].index(
                                   src.get("pillShape", ai.get("pillShape","oval"))))
    c1_hex = pv2.color_picker("Pill Color 1", value=src.get("c1", ai.get("c1","#94a3b8")))
    c2_hex = pv3.color_picker("Pill Color 2 (capsule 2nd half)", value=src.get("c2", ai.get("c2","#94a3b8")))
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Preview ──
    if name.strip():
        preview_drug = {
            "name": name.strip().upper(), "strength": strength, "din": din,
            "mfr": mfr, "commonName": common, "category": category,
            "drugClass": drug_class, "condition": condition,
            "brands": [b.strip() for b in brands_raw.split(",") if b.strip()],
            "isGeneric": is_generic, "odb": odb_status, "odbNotes": odb_notes,
            "copay": has_copay, "controlled": controlled, "opioid": opioid,
            "pillShape": pill_shape, "c1": c1_hex, "c2": c2_hex,
            "copaySteps": {"name": name.strip().upper(), "manufacturer": cp_mfr,
                           "phone": cp_phone, "website": cp_website, "steps": steps_out}
                          if has_copay else None,
        }
        st.markdown("**Preview:**")
        st.markdown(render_card(preview_drug, show_copay_steps=has_copay), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Save ──
    col_save, col_del, col_msg2 = st.columns([1, 1, 3])
    if col_save.button("💾 Save Medication", type="primary", use_container_width=True):
        if not name.strip():
            col_msg2.error("Drug Name is required.")
        else:
            new_entry = {
                "name": name.strip().upper(), "strength": strength.strip(),
                "din": din.strip(), "mfr": mfr.strip(),
                "commonName": common.strip(), "category": category,
                "drugClass": drug_class.strip(), "condition": condition.strip(),
                "brands": [b.strip() for b in brands_raw.split(",") if b.strip()],
                "isGeneric": is_generic, "odb": odb_status, "odbNotes": odb_notes.strip(),
                "copay": has_copay, "controlled": controlled, "opioid": opioid,
                "pillShape": pill_shape, "c1": c1_hex, "c2": c2_hex,
                "copaySteps": {"name": name.strip().upper(), "manufacturer": cp_mfr,
                               "phone": cp_phone, "website": cp_website, "steps": steps_out}
                              if has_copay else None,
            }
            if existing:
                # Update existing
                idx = drugs.index(existing)
                drugs[idx] = new_entry
                col_msg2.success(f"✅ Updated {new_entry['name']} {new_entry['strength']}.")
            else:
                drugs.append(new_entry)
                col_msg2.success(f"✅ Added {new_entry['name']} {new_entry['strength']}.")
            save_drugs(drugs)
            st.session_state.ai_data = {}
            st.rerun()

    if existing and col_del.button("🗑 Delete", use_container_width=True):
        drugs.remove(existing)
        save_drugs(drugs)
        col_msg2.success("Deleted.")
        st.rerun()

# ── Summary tab ───────────────────────────────────────────────────────────────
def tab_summary(drugs: list[dict]):
    st.markdown("### 📊 Store Summary")
    import pandas as pd

    df = pd.DataFrame([{
        "Drug Name":   d["name"],
        "Strength":    d.get("strength",""),
        "Common Name": d.get("commonName",""),
        "Category":    d.get("category",""),
        "Drug Class":  d.get("drugClass",""),
        "Brands":      ", ".join(d.get("brands",[])),
        "Generic":     "Yes" if d.get("isGeneric") else "No",
        "ODB Status":  d.get("odb",""),
        "Copay Card":  "Yes" if d.get("copay") else "No",
        "Controlled":  "Yes" if d.get("controlled") else "No",
        "Opioid":      "Yes" if d.get("opioid") else "No",
    } for d in drugs])

    # ODB breakdown
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Medications", len(drugs))
    s2.metric("🟢 ODB Covered", sum(1 for d in drugs if d.get("odb")=="Covered"))
    s3.metric("⭐ With Copay Cards", sum(1 for d in drugs if d.get("copay")))

    # Category breakdown
    st.markdown("#### By Category")
    cat_counts = df["Category"].value_counts().reset_index()
    cat_counts.columns = ["Category","Count"]
    st.bar_chart(cat_counts.set_index("Category"))

    st.markdown("#### Full Medication Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Export
    csv = df.to_csv(index=False).encode()
    st.download_button("📥 Download CSV", csv, "medications.csv", "text/csv")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="MedNavigator — Shoppers #1221",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    st.markdown("""
<div class="med-header">
  <div style="font-size:32px">💊</div>
  <div>
    <h1>MedNavigator</h1>
    <p>Tony Huynh Drugs Ltd · Shoppers Drug Mart #1221 · Brooklin, ON</p>
  </div>
</div>""", unsafe_allow_html=True)

    drugs = load_drugs()

    tab1, tab2, tab3 = st.tabs(["💊 Dashboard", "➕ Add / Edit Medication", "📊 Summary & Export"])

    with tab1:
        tab_dashboard(drugs)
    with tab2:
        tab_add_edit(drugs)
    with tab3:
        tab_summary(drugs)

if __name__ == "__main__":
    main()
