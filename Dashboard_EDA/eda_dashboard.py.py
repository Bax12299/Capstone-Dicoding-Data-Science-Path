import streamlit as st
import pandas as pd
import numpy as np
import ast
import re
import plotly.graph_objects as go
from collections import Counter

st.set_page_config(
    page_title="IT Job Market: EDA Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

:root {
    --accent:       #7C3AED;
    --accent-light: #F5F3FF;
    --accent-mid:   #EDE9FE;
    --accent-dark:  #5B21B6;
    --text:         #0F172A;
    --text-muted:   #64748B;
    --border:       #E2E8F0;
    --bg:           #FFFFFF;
    --bg-2:         #F8FAFC;
    --bg-3:         #F1F5F9;
    --green:        #10B981;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text);
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; max-width: 1440px; }

/*  Page header  */
.page-header { padding: 2rem 0 1.25rem; margin-bottom: 1.5rem; }
.page-header h1 {
    font-size: 1.75rem; font-weight: 700; color: var(--text);
    margin: 0 0 0.3rem; letter-spacing: -0.5px;
}
.page-header p { color: var(--text-muted); font-size: 0.875rem; margin: 0; }

/*  Nav bar  */
.nav-bar {
    display: flex; gap: 0.4rem; flex-wrap: wrap;
    padding: 0.65rem 0.875rem;
    background: var(--bg-2); border: 1px solid var(--border);
    border-radius: 12px; margin-bottom: 2rem; align-items: center;
}
.nav-label { font-size: 0.73rem; font-weight: 600; color: #94A3B8; padding-right: 0.4rem; white-space: nowrap; }
.nav-btn {
    display: inline-flex; align-items: center; gap: 0.35rem;
    padding: 0.38rem 0.85rem; border-radius: 7px;
    font-size: 0.78rem; font-weight: 600; color: var(--text-muted);
    background: transparent; border: 1px solid transparent;
    cursor: pointer; text-decoration: none; white-space: nowrap;
}
.nav-btn:hover { background: white; border-color: var(--border); color: var(--text); }
.bq-num {
    background: var(--accent); color: white;
    font-size: 0.62rem; font-weight: 700;
    padding: 2px 5px; border-radius: 4px;
    font-family: 'DM Mono', monospace;
}

/*  Metric cards  */
.metric-row { display: flex; gap: 0.75rem; margin-bottom: 2rem; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 140px;
    background: white; border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem 1.2rem;
}
.metric-card .label {
    font-size: 0.68rem; color: var(--text-muted); font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.35rem;
}
.metric-card .value {
    font-size: 1.65rem; font-weight: 700; color: var(--accent);
    line-height: 1; letter-spacing: -1px;
}
.metric-card .sub { font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem; }

/*  Section anchor (offset for fixed nav)  */
.section-anchor { display: block; position: relative; top: -72px; visibility: hidden; }

/*  Section header  */
.section-header {
    display: flex; align-items: center; gap: 0.8rem;
    margin-bottom: 1.25rem; padding: 1.1rem 1.25rem;
    background: var(--bg-2); border-radius: 10px;
    border-left: 3px solid var(--accent);
}
.section-header .bq-tag {
    background: var(--accent); color: white;
    font-size: 0.65rem; font-weight: 700; padding: 3px 8px;
    border-radius: 5px; white-space: nowrap; margin-top: 3px;
    font-family: 'DM Mono', monospace; letter-spacing: 0.3px;
    align-self: center;
}
.section-header h2 {
    font-size: 0.95rem; font-weight: 600; color: var(--text);
    margin: 0 0 0.18rem; letter-spacing: -0.2px;
}
.section-header p { font-size: 0.8rem; color: var(--text-muted); margin: 0; line-height: 1.5; }

/*  Insight box  */
.insight-box {
    background: var(--bg-2); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: 8px;
    padding: 0.85rem 1rem; margin-top: 0.875rem;
    font-size: 0.835rem; color: var(--text); line-height: 1.65;
}
.insight-box strong { color: var(--accent-dark); }

/*  Rank list item  */
.rank-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0.8rem; border-radius: 7px;
    margin-bottom: 0.4rem; border: 1px solid;
}

/*  Divider  */
.section-divider { border: none; border-top: 1px solid var(--border); margin: 2.25rem 0; }

/*  Control row  */
.control-row {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.75rem 1rem; background: var(--bg-2);
    border: 1px solid var(--border); border-radius: 8px;
    margin-bottom: 1rem;
}
.control-label { font-size: 0.78rem; font-weight: 600; color: var(--text-muted); white-space: nowrap; }

/*  Sort badge  */
.sort-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.3rem 0.7rem; border-radius: 6px;
    font-size: 0.73rem; font-weight: 600;
    background: var(--accent-light); color: var(--accent);
    border: 1px solid var(--accent-mid);
}

/* Streamlit slider tweak */
div[data-testid="stSlider"] > div { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)


# Data 
@st.cache_data
def load_data():
    df = pd.read_csv("df_eda_fix.csv")

    def parse_skills(s):
        try:
            return ast.literal_eval(s)
        except Exception:
            return []

    def extract_country(loc):
        if not isinstance(loc, str):
            return "Unknown"
        loc_clean = re.sub(r"\(.*?\)", "", loc).strip()
        parts = [p.strip() for p in loc_clean.split(",")]
        return parts[-1].strip() if parts else "Unknown"

    df["skills_parsed"] = df["skills_list"].apply(parse_skills)
    df["country"]       = df["location"].apply(extract_country)
    return df

df = load_data()

all_skills_flat = [s for row in df["skills_parsed"] for s in row]
skill_freq      = Counter(all_skills_flat)
total_jobs      = len(df)
total_skills    = len(set(all_skills_flat))
top_skill       = skill_freq.most_common(1)[0][0].title()
max_kw          = int(df["keyword"].nunique())

# Warna plot
PURPLE      = "#7C3AED"
PURPLE_DARK = "#5B21B6"
PURPLE_LITE = "#EDE9FE"
PURPLE_MID  = "#A78BFA"
GREY        = "#94A3B8"

def base_layout(title="", margin=None):
    return dict(
        title=dict(
            text=title,
            font=dict(size=13, color="#0F172A", family="DM Sans"),
            x=0, pad=dict(l=0, b=12),
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="DM Sans", color="#0F172A"),
        margin=margin if margin is not None else dict(l=0, r=0, t=42, b=0),
    )

AXIS_STYLE = dict(showgrid=True, gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=10))

def apply_base_axes(fig):
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    return fig


# Page header 
st.markdown("""
<div class="page-header">
    <h1>IT Job Market: Exploratory Analysis</h1>
    <p>Analisis 3.994 lowongan kerja IT dari LinkedIn Global &nbsp;|&nbsp; 105 kategori pekerjaan</p>
</div>
""", unsafe_allow_html=True)

# Nav
st.markdown("""
<div class="nav-bar">
    <span class="nav-label">Lompat ke:</span>
    <a class="nav-btn" href="#bq1"><span class="bq-num">BQ1</span> Skill Terpopuler</a>
    <a class="nav-btn" href="#bq2"><span class="bq-num">BQ2</span> Remote vs On-site</a>
    <a class="nav-btn" href="#bq3"><span class="bq-num">BQ3</span> Kompleksitas Skill</a>
    <a class="nav-btn" href="#bq4"><span class="bq-num">BQ4</span> Skill Distinktif</a>
    <a class="nav-btn" href="#bq5"><span class="bq-num">BQ5</span> Remote Premium</a>
    <a class="nav-btn" href="#bq6"><span class="bq-num">BQ6</span> Co-occurrence</a>
</div>
""", unsafe_allow_html=True)

# Metrics
st.markdown(f"""
<div class="metric-row">
    <div class="metric-card">
        <div class="label">Total Lowongan</div>
        <div class="value">{total_jobs:,}</div>
        <div class="sub">setelah dibersihkan</div>
    </div>
    <div class="metric-card">
        <div class="label">Kategori pekerjaan</div>
        <div class="value">105</div>
        <div class="sub">kategori</div>
    </div>
    <div class="metric-card">
        <div class="label">Skill Unik</div>
        <div class="value">{total_skills:,}</div>
        <div class="sub">dari total {total_jobs} lowongan</div>
    </div>
    <div class="metric-card">
        <div class="label">Skill Terpopuler</div>
        <div class="value" style="font-size:1.3rem;letter-spacing:0">{top_skill}</div>
        <div class="sub">muncul di {skill_freq.most_common(1)[0][1]:,} lowongan</div>
    </div>
    <div class="metric-card">
        <div class="label">Rata-rata Skill/Job</div>
        <div class="value">{df['n_skills'].mean():.1f}</div>
        <div class="sub">median: {int(df['n_skills'].median())}</div>
    </div>
</div>
""", unsafe_allow_html=True)



# BQ 1

st.markdown('<a class="section-anchor" id="bq1"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="bq-tag">BQ 1</span>
    <div>
        <h2>Apa 30 skill yang paling banyak diminta berdasarkan dataset lowongan IT LinkedIn yang dikumpulkan?</h2>
        <p>Objektif : mengidentifikasi skill dengan kemunculan tertinggi di seluruh 3.994 lowongan LinkedIn.</p>
    </div>
</div>
""", unsafe_allow_html=True)

col_ctrl1, _ = st.columns([1, 3])
with col_ctrl1:
    top_n_bq1 = st.slider("Tampilkan top N skill", min_value=10, max_value=50, value=25, step=5, key="bq1_n")

top_skills_df = pd.DataFrame(skill_freq.most_common(top_n_bq1), columns=["skill", "count"])
top_skills_df["skill"] = top_skills_df["skill"].str.title()
top_skills_df["pct"]   = (top_skills_df["count"] / total_jobs * 100).round(1)
bar_colors_bq1 = [PURPLE if i < 5 else "#C4B5FD" for i in range(len(top_skills_df))]

fig_bq1 = go.Figure(go.Bar(
    x=top_skills_df["count"].iloc[::-1].values,
    y=top_skills_df["skill"].iloc[::-1].values,
    orientation="h",
    marker_color=bar_colors_bq1[::-1],
    text=[f"{p}%" for p in top_skills_df["pct"].iloc[::-1].values],
    textposition="outside",
    textfont=dict(size=10, color="#64748B"),
    hovertemplate="<b>%{y}</b><br>%{x} lowongan<extra></extra>",
))
chart_height_bq1 = max(320, top_n_bq1 * 22)
fig_bq1.update_layout(
    **base_layout(f"Top {top_n_bq1} Skill Paling Banyak Diminta"),
    height=chart_height_bq1,
    xaxis_title="Jumlah Lowongan",
    yaxis_title=None,
)
fig_bq1.update_xaxes(range=[0, top_skills_df["count"].max() * 1.15])
apply_base_axes(fig_bq1)
st.plotly_chart(fig_bq1, use_container_width=True)

top5_str = ", ".join([s.title() for s in [sk for sk, _ in skill_freq.most_common(5)]])
st.markdown(f"""
<div class="insight-box">
    <strong>Insight:</strong> Lima skill teratas dari total {total_skills} skill adalah <strong>{top5_str}</strong>, skill tersebut mendominasi
    permintaan pasar IT global. Python muncul di <strong>{skill_freq['python']:,} lowongan
    ({skill_freq['python']/total_jobs*100:.0f}%)</strong> dari total dataset, menjadikannya
    skill yang hampir wajib dimiliki lintas kategori pekerjaan. SQL tetap relevan karena hampir
    semua peran yang berurusan dengan data membutuhkannya, sementara Kubernetes dan Terraform
    mencerminkan tingginya permintaan untuk profil yang menguasai infrastruktur cloud modern.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)



# BQ 2
st.markdown('<a class="section-anchor" id="bq2"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="bq-tag">BQ 2</span>
    <div>
        <h2>Bagaimana persentase distribusi work type (Remote, Hybrid, On-site) pada 20 kategori jabatan IT dengan volume lowongan tertinggi berdasarkan dataset yang dikumpulkan?</h2>
        <p>Objektif : memetakan distribusi Remote, Hybrid, dan On-site untuk setiap kategori pekerjaan IT.
    </div>
</div>
""", unsafe_allow_html=True)

# Controls BQ2 
col_c1, col_c2, col_c3 = st.columns([1, 1, 2])
with col_c1:
    top_n_bq2 = st.slider(
        "Jumlah kategori (Top N)",
        min_value=5, max_value=min(40, max_kw), value=20, step=5,
        key="bq2_n",
        help="Pilih berapa banyak kategori pekerjaan yang ditampilkan, diurutkan berdasarkan jumlah lowongan terbanyak."
    )
with col_c2:
    sort_by_bq2 = st.selectbox(
        "Urutkan berdasarkan",
        options=["Remote (%)", "Hybrid (%)", "On-site (%)", "Jumlah lowongan"],
        index=0,
        key="bq2_sort"
    )

# Compute 
top_kw_bq2 = df["keyword"].value_counts().head(top_n_bq2).index.tolist()
df_wt       = df[df["keyword"].isin(top_kw_bq2)]

wt_pivot = (
    df_wt.groupby(["keyword", "work_type"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=["Remote", "Hybrid", "On-site"], fill_value=0)
)
wt_pct = wt_pivot.div(wt_pivot.sum(axis=1), axis=0).mul(100).round(1)

sort_map = {
    "Remote (%)":         "Remote",
    "Hybrid (%)":         "Hybrid",
    "On-site (%)":        "On-site",
    "Jumlah lowongan":    None,
}
sort_col = sort_map[sort_by_bq2]
if sort_col:
    wt_pct = wt_pct.sort_values(sort_col, ascending=True)
else:
    ordered = df["keyword"].value_counts().head(top_n_bq2).index.tolist()
    wt_pct  = wt_pct.reindex(ordered[::-1])

# Chart 
colors_wt      = {"Remote": PURPLE, "Hybrid": PURPLE_MID, "On-site": "#DDD6FE"}
chart_h_bq2    = max(50, top_n_bq2 * 24)

fig_bq2 = go.Figure()
for wt in ["On-site", "Hybrid", "Remote"]:
    if wt not in wt_pct.columns:
        continue
    fig_bq2.add_trace(go.Bar(
        name=wt,
        y=wt_pct.index,
        x=wt_pct[wt],
        orientation="h",
        marker_color=colors_wt[wt],
        hovertemplate=f"<b>%{{y}}</b><br>{wt}: %{{x:.1f}}%<extra></extra>",
    ))
fig_bq2.update_layout(
    **base_layout(f"Distribusi Work Type per Kategori pekerjaan (Top {top_n_bq2}, diurutkan: {sort_by_bq2})"),
    barmode="stack",
    height=chart_h_bq2,
    legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="left", x=0,
                font=dict(size=11)),
    xaxis_title="Persentase (%)",
    yaxis_title=None,
)
apply_base_axes(fig_bq2)
st.plotly_chart(fig_bq2, use_container_width=True)

# Side summary: dynamic top 5 
col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown("**Top 5 Kategori Pekerjaan Paling Remote-Friendly**")
    top5_remote = wt_pct["Remote"].sort_values(ascending=False).head(5)
    for kw, pct in top5_remote.items():
        st.markdown(f"""
        <div class="rank-item" style="background:#F5F3FF;border-color:#EDE9FE;">
            <span style="font-size:0.82rem;font-weight:600;color:#0F172A;">{kw}</span>
            <span style="font-size:0.82rem;font-weight:700;color:{PURPLE};">{pct:.0f}%</span>
        </div>
        """, unsafe_allow_html=True)

with col_r2:
    st.markdown("**Top 5 Kategori Pekerjaan Paling On-site**")
    top5_onsite = wt_pct["On-site"].sort_values(ascending=False).head(5)
    for kw, pct in top5_onsite.items():
        st.markdown(f"""
        <div class="rank-item" style="background:#F8FAFC;border-color:#E2E8F0;">
            <span style="font-size:0.82rem;font-weight:600;color:#0F172A;">{kw}</span>
            <span style="font-size:0.82rem;font-weight:700;color:#64748B;">{pct:.0f}%</span>
        </div>
        """, unsafe_allow_html=True)

remote_leader = wt_pct["Remote"].idxmax()
onsite_leader = wt_pct["On-site"].idxmax()
st.markdown(f"""
<div class="insight-box">
    <strong>Insight:</strong> Dalam top {top_n_bq2} kategori, pekerjaan berbasis infrastruktur
    dan otomasi seperti <strong>{remote_leader}</strong> memiliki persentase remote tertinggi, kebanyakan
    pekerjaan ini dapat dilakukan sepenuhnya dari jarak jauh via cloud. Sebaliknya,
    <strong>{onsite_leader}</strong> cenderung on-site karena membutuhkan akses fisik ke
    perangkat keras atau koordinasi langsung dengan tim non-teknis.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)



# BQ 3
st.markdown('<a class="section-anchor" id="bq3"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="bq-tag">BQ 3</span>
    <div>
        <h2>Kategori jabatan IT mana yang memiliki rata-rata jumlah skill tertinggi per lowongan berdasarkan dataset yang dikumpulkan?</h2>
        <p>Objektif : Mengukur rata-rata jumlah skill yang dicantumkan per lowongan untuk setiap kategori pekerjaan.</p>
    </div>
</div>
""", unsafe_allow_html=True)

col_c3a, _ = st.columns([1, 3])
with col_c3a:
    top_n_bq3 = st.slider("Tampilkan top N kategori", min_value=5, max_value=30, value=15, step=5, key="bq3_n")

skill_complexity = (
    df.groupby("keyword")["n_skills"]
    .agg(["mean", "median", "std", "count"])
    .round(2)
    .reset_index()
    .rename(columns={"mean": "rata_rata", "median": "median_val", "std": "std_dev", "count": "n_jobs"})
    .sort_values("rata_rata", ascending=False)
    .reset_index(drop=True)
)
top_complex = skill_complexity.head(top_n_bq3).copy()

n_c          = len(top_complex)
bar_colors_c = [PURPLE if i < 5 else "#C4B5FD" if i < 10 else PURPLE_LITE for i in range(n_c)]

fig_bq3 = go.Figure(go.Bar(
    x=top_complex["rata_rata"].iloc[::-1].values,
    y=top_complex["keyword"].iloc[::-1].values,
    orientation="h",
    marker_color=bar_colors_c[::-1],
    error_x=dict(
        type="data",
        array=top_complex["std_dev"].iloc[::-1].fillna(0).values.tolist(),
        color="#CBD5E1", thickness=1.5, width=4,
    ),
    text=[f"{v:.1f}" for v in top_complex["rata_rata"].iloc[::-1].values],
    textposition="outside",
    textfont=dict(size=10, color="#64748B"),
    hovertemplate="<b>%{y}</b><br>Rata-rata: %{x:.1f} skill<extra></extra>",
))
fig_bq3.update_layout(
    **base_layout(f"Rata-rata Jumlah Skill per Lowongan (Top {top_n_bq3} Kategori)"),
    height=max(320, top_n_bq3 * 26),
    xaxis_title="Rata-rata Jumlah Skill",
    yaxis_title=None,
)
fig_bq3.update_xaxes(range=[0, top_complex["rata_rata"].max() * 1.2])
apply_base_axes(fig_bq3)

col_bq3a, col_bq3b = st.columns([1.6, 1])

with col_bq3a:
    st.plotly_chart(fig_bq3, use_container_width=True)

with col_bq3b:
    st.markdown("**Distribusi skill — semua kategori**")
    fig_box = go.Figure(go.Box(
        y=df["n_skills"],
        marker_color=PURPLE, line_color=PURPLE_DARK, fillcolor=PURPLE_LITE,
        boxmean=True, name="n_skills",
        hovertemplate="n_skills: %{y}<extra></extra>",
    ))
    fig_box.update_layout(
        **base_layout("Distribusi Jumlah Skill per Lowongan"),
        height=240, showlegend=False, yaxis_title="Jumlah Skill",
    )
    apply_base_axes(fig_box)
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown(f"**Top {min(5, top_n_bq3)} kategori skill terbanyak**")
    for _, row in top_complex.head(5).iterrows():
        st.markdown(f"""
        <div class="rank-item" style="background:#F5F3FF;border-color:#EDE9FE;">
            <span style="font-size:0.79rem;font-weight:600;color:#0F172A;">{row['keyword']}</span>
            <span style="font-size:0.8rem;font-weight:700;color:{PURPLE};">{row['rata_rata']:.1f} skill</span>
        </div>
        """, unsafe_allow_html=True)

hardest = top_complex.iloc[0]["keyword"]
easiest = skill_complexity.iloc[-1]["keyword"]
st.markdown(f"""
<div class="insight-box">
    <strong>Insight:</strong> <strong>{hardest}</strong> menuntut jumlah skill rata-rata
    tertinggi per lowongan, hal ini mencerminkan penguasaan toolchain yang luas mulai dari
    infrastruktur, orkestrasi container, hingga pemrograman.
    Sebaliknya, kategori seperti <strong>{easiest}</strong> biasanya hanya mencantumkan
    beberapa skill spesifik. Informasi ini berguna untuk mengukur seberapa luas
    persiapan yang dibutuhkan untuk kategori tertentu.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)



# BQ 4
st.markdown('<a class="section-anchor" id="bq4"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="bq-tag">BQ 4</span>
    <div>
        <h2>Skill apa yang memiliki distinctiveness ratio tertinggi pada masing-masing kategori jabatan IT berdasarkan dataset yang dikumpulkan?</h2>
        <p>Objektif : Mengukur distinctiveness ratio: seberapa khas sebuah skill untuk kategori tertentu dibanding rata-rata global.</p>
    </div>
</div>
""", unsafe_allow_html=True)

focus_jobs = [
    "Data Scientist", "Data Engineer", "Data Analyst",
    "DevOps Engineer", "Machine Learning Engineer", "Cyber Security Analyst",
    "Back End Developer", "Front End Developer", "Cloud Engineer", "Flutter Developer",
]

distinct_data = {}
for kw in focus_jobs:
    sub = df[df["keyword"] == kw]
    if len(sub) == 0:
        continue
    job_flat    = [s for row in sub["skills_parsed"] for s in row]
    job_freq_kw = Counter(job_flat)
    ranked = []
    for sk, cnt in job_freq_kw.most_common(80):
        g_rate = skill_freq[sk] / total_jobs if total_jobs > 0 else 0
        ratio  = (cnt / len(sub)) / (g_rate + 0.001)
        if ratio > 1.5 and cnt >= 3:
            ranked.append((sk, round(ratio, 2)))
        if len(ranked) >= 5:
            break
    distinct_data[kw] = ranked

all_d_skills = []
for items in distinct_data.values():
    for sk, _ in items[:4]:
        if sk not in all_d_skills:
            all_d_skills.append(sk)

valid_jobs = [kw for kw in focus_jobs if kw in distinct_data and len(distinct_data[kw]) > 0]
heat_rows  = []
for kw in valid_jobs:
    row_d = {sk: 0.0 for sk in all_d_skills}
    for sk, ratio in distinct_data[kw]:
        if sk in row_d:
            row_d[sk] = ratio
    heat_rows.append([row_d[sk] for sk in all_d_skills])

if heat_rows and all_d_skills:
    heat_df = pd.DataFrame(heat_rows, index=valid_jobs, columns=all_d_skills)
    heat_df.columns = [c.title() for c in heat_df.columns]

    fig_bq4 = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0, "#FFFFFF"], [0.3, PURPLE_LITE], [0.7, PURPLE_MID], [1, PURPLE]],
        hovertemplate="<b>%{y}</b><br>Skill: %{x}<br>Ratio: %{z:.1f}x<extra></extra>",
        text=[[f"{v:.1f}" if v > 0 else "" for v in row] for row in heat_df.values],
        texttemplate="%{text}",
        textfont=dict(size=9),
        showscale=True,
        colorbar=dict(title="Ratio", tickfont=dict(size=10)),
    ))
    fig_bq4.update_layout(
        **base_layout(
            "Skill Khas per Kategori pekerjaan",
            margin=dict(l=0, r=60, t=42, b=80),
        ),
        height=400,
    )
    apply_base_axes(fig_bq4)
    fig_bq4.update_xaxes(tickangle=-35, tickfont=dict(size=10))
    fig_bq4.update_yaxes(tickfont=dict(size=10))
    st.plotly_chart(fig_bq4, use_container_width=True)
else:
    st.info("Data tidak cukup untuk menampilkan heatmap distinctiveness.")

st.markdown("""
<div class="insight-box">
    <strong>Insight:</strong> Heatmap ini membaca seberapa eksklusif suatu skill untuk
    satu kategori pekerjaan. Nilai <strong>1x</strong> berarti skill itu biasa muncul di mana
    saja. Nilai tinggi berarti skill itu sangat identik dengan pekerjaan tersebut, sebagai contoh <strong>Dart dan Flutter</strong> hampir hanya muncul di lowongan Flutter Developer,
    dan <strong>PyTorch</strong> sangat khas untuk Machine Learning Engineer.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)



# BQ 5
st.markdown('<a class="section-anchor" id="bq5"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="bq-tag">BQ 5</span>
    <div>
        <h2>Apakah rata-rata jumlah skill lowongan Remote secara statistik lebih tinggi dibanding On-site berdasarkan dataset yang dikumpulkan?</h2>
        <p>Objektif : Membandingkan jumlah skill yang diminta berdasarkan tipe kerja untuk melihat apakah
        ada "skill premium" pada posisi remote.</p>
    </div>
</div>
""", unsafe_allow_html=True)

wt_order = ["Remote", "Hybrid", "On-site"]
wt_stats = (
    df.groupby("work_type")["n_skills"]
    .agg(["mean", "median", "std"])
    .round(2)
    .reindex(wt_order)
    .fillna(0)
    .reset_index()
)

col_bq5a, col_bq5b = st.columns(2)

with col_bq5a:
    fig_bq5a = go.Figure(go.Bar(
        x=wt_stats["work_type"],
        y=wt_stats["mean"],
        marker_color=[PURPLE, PURPLE_MID, PURPLE_LITE],
        text=[f"{v:.2f}" for v in wt_stats["mean"]],
        textposition="outside",
        textfont=dict(size=12, color="#0F172A"),
        error_y=dict(type="data", array=wt_stats["std"].fillna(0).tolist(),
                     color="#CBD5E1", thickness=1.5, width=6),
        hovertemplate="<b>%{x}</b><br>Rata-rata: %{y:.2f} skill<extra></extra>",
        width=0.5,
    ))
    fig_bq5a.update_layout(
        **base_layout("Rata-rata Skill per Tipe Kerja"),
        height=340, xaxis_title=None, yaxis_title="Rata-rata Jumlah Skill",
    )
    apply_base_axes(fig_bq5a)
    fig_bq5a.update_yaxes(range=[0, wt_stats["mean"].max() * 1.28])
    st.plotly_chart(fig_bq5a, use_container_width=True)

with col_bq5b:
    fig_bq5b = go.Figure()
    colors_v  = {"Remote": PURPLE, "Hybrid": PURPLE_MID, "On-site": "#C4B5FD"}
    for wt in wt_order:
        sub_wt = df[df["work_type"] == wt]["n_skills"]
        if len(sub_wt) == 0:
            continue
        fig_bq5b.add_trace(go.Violin(
            y=sub_wt, name=wt,
            box_visible=True, meanline_visible=True,
            fillcolor=colors_v.get(wt, GREY), opacity=0.7,
            line_color=PURPLE_DARK,
            hovertemplate=f"<b>{wt}</b><br>n_skills: %{{y}}<extra></extra>",
        ))
    fig_bq5b.update_layout(
        **base_layout("Distribusi Skill per Tipe Kerja"),
        height=340, showlegend=False, violingap=0.3,
        yaxis_title="Jumlah Skill", xaxis_title=None,
    )
    apply_base_axes(fig_bq5b)
    st.plotly_chart(fig_bq5b, use_container_width=True)

# Skill dominan di remote
remote_df = df[df["work_type"] == "Remote"]
onsite_df = df[df["work_type"] == "On-site"]
n_remote  = max(len(remote_df), 1)
n_onsite  = max(len(onsite_df), 1)

remote_skills   = [s for row in remote_df["skills_parsed"] for s in row]
onsite_skills   = [s for row in onsite_df["skills_parsed"] for s in row]
remote_freq_wt  = Counter(remote_skills)
onsite_freq_wt  = Counter(onsite_skills)

remote_distinct = []
for sk, cnt in remote_freq_wt.most_common(200):
    r_rate = cnt / n_remote
    o_rate = onsite_freq_wt.get(sk, 0) / n_onsite
    if r_rate > o_rate * 1.4 and cnt >= 10:
        remote_distinct.append((sk.title(), round(r_rate * 100, 1), round(o_rate * 100, 1)))
    if len(remote_distinct) >= 6:
        break

if remote_distinct:
    st.markdown("**Skill yang lebih dominan di lowongan Remote vs On-site:**")
    cols_rd = st.columns(len(remote_distinct))
    for i, (sk, r_pct, o_pct) in enumerate(remote_distinct):
        diff = r_pct - o_pct
        cols_rd[i].markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:9px;
                    padding:0.8rem 0.6rem;text-align:center;">
            <div style="font-size:0.73rem;font-weight:700;color:#0F172A;margin-bottom:0.3rem">{sk}</div>
            <div style="font-size:1rem;font-weight:700;color:{PURPLE};">{r_pct:.0f}%</div>
            <div style="font-size:0.67rem;color:#64748B;">remote</div>
            <div style="font-size:0.68rem;color:#10B981;margin-top:0.18rem;">+{diff:.0f}% vs on-site</div>
        </div>
        """, unsafe_allow_html=True)

remote_mean = remote_df["n_skills"].mean() if n_remote > 1 else 0
onsite_mean = onsite_df["n_skills"].mean() if n_onsite > 1 else 0
diff_pct    = ((remote_mean - onsite_mean) / onsite_mean * 100) if onsite_mean > 0 else 0

st.markdown(f"""
<div class="insight-box">
    <strong>Insight:</strong> Lowongan remote rata-rata mencantumkan
    <strong>{remote_mean:.1f} skill</strong> per lowongan, lebih tinggi
    <strong>{diff_pct:.0f}%</strong> dibanding lowongan on-site ({onsite_mean:.1f} skill).
    Ini mengindikasikan bahwa perusahaan yang membuka posisi remote cenderung mencari
    kandidat yang lebih self-sufficient secara teknis, karena tidak ada supervisor
    langsung di tempat kerja.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)



# BQ 6
st.markdown('<a class="section-anchor" id="bq6"></a>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="bq-tag">BQ 6</span>
    <div>
        <h2>Apa 20 pasangan skill dengan nilai co-occurrence tertinggi berdasarkan dataset lowongan IT LinkedIn yang dikumpulkan?</h2>
        <p>Objektif : Analisis co-occurrence untuk memahami "paket skill" yang umum dibutuhkan industri.</p>
    </div>
</div>
""", unsafe_allow_html=True)

col_c6a, col_c6b, _ = st.columns([1, 1, 2])
with col_c6a:
    top_n_pairs = st.slider("Top N pasangan skill", min_value=5, max_value=25, value=15, step=5, key="bq6_pairs")
with col_c6b:
    top_n_matrix = st.slider("Top N skill (matrix)", min_value=5, max_value=15, value=10, step=1, key="bq6_matrix")

pairs = Counter()
for skills in df["skills_parsed"]:
    uniq = list(set(skills))
    for i in range(len(uniq)):
        for j in range(i + 1, len(uniq)):
            pairs[tuple(sorted([uniq[i], uniq[j]]))] += 1

top_pairs = pairs.most_common(top_n_pairs)

col_bq6a, col_bq6b = st.columns([1.2, 1])

with col_bq6a:
    pairs_df = pd.DataFrame(
        [(f"{a.title()} + {b.title()}", cnt) for (a, b), cnt in top_pairs],
        columns=["pair", "count"],
    )
    bc6 = [PURPLE if i < 5 else PURPLE_LITE for i in range(len(pairs_df))]
    fig_bq6a = go.Figure(go.Bar(
        x=pairs_df["count"].iloc[::-1].values,
        y=pairs_df["pair"].iloc[::-1].values,
        orientation="h",
        marker_color=bc6[::-1],
        text=pairs_df["count"].iloc[::-1].values,
        textposition="outside",
        textfont=dict(size=10, color="#64748B"),
        hovertemplate="<b>%{y}</b><br>%{x} lowongan<extra></extra>",
    ))
    fig_bq6a.update_layout(
        **base_layout(f"Top {top_n_pairs} Pasangan Skill yang Sering Muncul Bersama"),
        height=max(300, top_n_pairs * 28),
        xaxis_title="Jumlah Lowongan", yaxis_title=None,
    )
    fig_bq6a.update_xaxes(range=[0, pairs_df["count"].max() * 1.2])
    apply_base_axes(fig_bq6a)
    st.plotly_chart(fig_bq6a, use_container_width=True)

with col_bq6b:
    top_n_sk    = [sk for sk, _ in skill_freq.most_common(top_n_matrix)]
    n_sk        = len(top_n_sk)
    comat       = np.zeros((n_sk, n_sk))
    for skills in df["skills_parsed"]:
        skill_set = set(skills)
        for i, si in enumerate(top_n_sk):
            for j, sj in enumerate(top_n_sk):
                if si in skill_set and sj in skill_set and i != j:
                    comat[i][j] += 1

    labels   = [s.title() for s in top_n_sk]
    fig_bq6b = go.Figure(go.Heatmap(
        z=comat, x=labels, y=labels,
        colorscale=[[0, "#FFFFFF"], [0.4, PURPLE_LITE], [1, PURPLE]],
        hovertemplate="<b>%{y} + %{x}</b><br>%{z:.0f} lowongan<extra></extra>",
        text=[[f"{int(v)}" if v > 0 else "" for v in row] for row in comat],
        texttemplate="%{text}",
        textfont=dict(size=8),
        showscale=False,
    ))
    fig_bq6b.update_layout(
        **base_layout(f"Co-occurrence Matrix — Top {top_n_matrix} Skill",
                      margin=dict(l=0, r=0, t=42, b=60)),
        height=max(300, top_n_pairs * 28),
    )
    apply_base_axes(fig_bq6b)
    fig_bq6b.update_xaxes(tickangle=-35, tickfont=dict(size=9), side="bottom")
    fig_bq6b.update_yaxes(tickfont=dict(size=9), autorange="reversed")
    st.plotly_chart(fig_bq6b, use_container_width=True)

if top_pairs:
    top_pair_a, top_pair_b = top_pairs[0][0]
    top_pair_cnt           = top_pairs[0][1]
    st.markdown(f"""
<div class="insight-box">
    <strong>Insight:</strong> Pasangan skill paling dominan adalah
    <strong>{top_pair_a.title()} + {top_pair_b.title()}</strong> yang muncul bersama
    di <strong>{top_pair_cnt} lowongan</strong>. Menguasai Python saja tidak cukup. Berdasarkan data lowongan,
    perusahaan mengharapkan Python dikombinasikan dengan SQL untuk kebutuhan data,
    atau Kubernetes/Terraform untuk kebutuhan infrastruktur. Co-occurrence matrix
    memperlihatkan klaster skill: data (Python, SQL, ML) dan DevOps (Docker, Kubernetes, Terraform).
</div>
""", unsafe_allow_html=True)


# Footer 
st.markdown("""
<hr class='section-divider'>
<div style="text-align:center;padding:0.875rem 0 1.75rem;color:#94A3B8;
            font-size:0.75rem;font-family:'DM Mono',monospace;letter-spacing:0.3px;">
    Data: LinkedIn Global Job Postings &nbsp;|&nbsp; 3.994 lowongan &nbsp;|&nbsp; 105 kategori pekerjaan
</div>
""", unsafe_allow_html=True)