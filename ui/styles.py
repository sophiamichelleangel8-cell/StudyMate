import html as _html

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Great+Vibes&family=DM+Sans:wght@400;500;600&display=swap');
:root{--blue:#DCE4EF;--butter:#C9D3E2;--cream:#F8FAFD;--sblue:#A0ADC2;--yellow:#C9D3E2;
--text:#1F2B3D;--muted:#5C6B82;--accent:#394E6E;--border:rgba(57,78,110,.20);}
.stApp{background:var(--blue);color:var(--text);font-family:'DM Sans',sans-serif;}
.stApp p,.stApp li,.stApp label,.stApp input,.stApp textarea,.stApp button{font-family:'DM Sans',sans-serif;}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer,[data-testid="stDecoration"]{visibility:hidden;display:none;}
.block-container{padding-top:2.4rem;padding-bottom:4rem;max-width:1080px;}
.stApp h1,.stApp h2,.stApp h3{font-family:'Playfair Display',Georgia,serif;color:var(--text);letter-spacing:-.01em;font-weight:600;}
.stApp h1{font-size:2.5rem;line-height:1.15;padding-top:.2rem;}
.stApp h3{font-size:1.4rem;margin-top:1.4rem;}
[data-testid="stSidebar"]{background:var(--butter);border-right:1px solid var(--border);}
.sm-brand{font-family:'Playfair Display',serif;font-size:1.9rem;font-weight:700;color:var(--text);line-height:1.1;}
.sm-tag{color:var(--muted);font-size:.82rem;margin:.2rem 0 1.4rem 0;}
.sm-script{font-family:'Great Vibes',cursive;font-size:2rem;color:var(--accent);line-height:1.2;}
.sm-sub{color:var(--muted);font-size:1.02rem;max-width:640px;margin-bottom:1.4rem;}
.sm-card{background:var(--cream);border:1px solid var(--border);border-radius:14px;padding:1.2rem 1.4rem;box-shadow:0 2px 10px rgba(75,98,112,.08);margin-bottom:.8rem;}
.sm-card-y{background:var(--butter);}
.sm-stat-n{font-family:'Playfair Display',serif;font-size:2.4rem;font-weight:600;color:var(--text);line-height:1.1;}
.sm-stat-l{color:var(--muted);font-size:.9rem;margin-top:.2rem;}
.sm-doc-title{font-family:'Playfair Display',serif;font-size:1.25rem;font-weight:600;}
.sm-doc-meta{color:var(--muted);font-size:.9rem;margin-top:.15rem;}
.sm-ok{color:#2f6b4f;font-weight:600;margin-right:.6rem;}
.sm-act-t{font-weight:600;}
.sm-act-d{color:var(--muted);font-size:.9rem;}
.sm-chip{display:inline-block;background:var(--cream);border:1px solid var(--border);border-radius:999px;padding:.25rem .8rem;margin:0 .4rem .4rem 0;font-size:.9rem;}
.sm-row{display:flex;justify-content:space-between;font-size:.95rem;margin-top:.7rem;}
.sm-bar{background:rgba(75,98,112,.12);border-radius:999px;height:9px;overflow:hidden;}
.sm-bar>div{background:var(--accent);height:9px;border-radius:999px;}
.sm-big{font-family:'Playfair Display',serif;font-size:3.6rem;font-weight:600;line-height:1;}
.sm-q{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:600;line-height:1.4;}
.sm-qn{color:var(--muted);font-size:.88rem;margin-bottom:.3rem;}
.sm-good{color:#2f6b4f;font-weight:600;}
.sm-bad{color:#a24b3f;font-weight:600;}
.sm-ans{background:var(--yellow);border-radius:12px;padding:1rem 1.2rem;margin-top:1rem;}
.stButton>button{border-radius:10px;border:1px solid var(--border);background:var(--cream);color:var(--accent);font-weight:500;padding:.55rem 1rem;transition:background .15s,border-color .15s;}
.stButton>button p{color:inherit;}
.stButton>button:hover{background:var(--yellow);border-color:var(--accent);color:var(--text);}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{background:var(--accent);color:#FFFDF5;border-color:var(--accent);}
.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="stBaseButton-primary"]:hover{background:#3b4f5b;color:#FFFFFF;}
.stButton>button:disabled{opacity:.45;}
[data-testid="stSidebar"] .stButton>button{background:transparent;border:none;justify-content:flex-start;text-align:left;color:var(--accent);padding:.5rem .8rem;}
[data-testid="stSidebar"] .stButton>button p{text-align:left;}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(187,217,243,.55);color:var(--text);}
[data-testid="stSidebar"] .stButton>button[kind="primary"],[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]{background:var(--sblue);color:var(--text);font-weight:600;border:none;}
[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover,[data-testid="stSidebar"] .stButton>button[data-testid="stBaseButton-primary"]:hover{background:var(--sblue);color:var(--text);}
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--cream);border-radius:14px;border-color:var(--border);}
[data-testid="stChatMessage"]{background:var(--cream);border:1px solid var(--border);border-radius:14px;padding:.9rem 1.1rem;}
[data-testid="stRadio"] label[data-baseweb="radio"]{background:var(--cream);border:1px solid var(--border);border-radius:10px;padding:.6rem .9rem;margin-bottom:.4rem;width:100%;}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover{background:var(--yellow);}
[data-testid="stFileUploaderDropzone"]{background:var(--cream);border:1.5px dashed var(--accent);border-radius:12px;}
[data-baseweb="select"]>div{background:var(--cream);}
[data-testid="stAlert"]{border-radius:12px;}
@media (max-width:640px){
.block-container{padding:1.2rem 1rem 3rem;}
.stApp h1{font-size:1.9rem;}
.sm-stat-n{font-size:1.8rem;}
.sm-big{font-size:2.8rem;}
}
.sm-slide{background:#394E6E;color:#DCE4EF;border-radius:14px;padding:2.4rem 2.6rem;min-height:340px;box-shadow:0 6px 22px rgba(57,78,110,.25);}
.sm-slide-n{color:#A0ADC2;font-size:.88rem;margin-bottom:.8rem;}
.sm-slide-t{font-family:'Playfair Display',serif;font-size:2.1rem;font-weight:700;line-height:1.2;color:#DCE4EF;margin-bottom:1.2rem;}
.sm-slide ul{margin:0;padding-left:1.2rem;}
.sm-slide li{font-size:1.12rem;line-height:1.6;margin-bottom:.55rem;color:#DCE4EF;}
.sm-dots{text-align:center;margin:.9rem 0 .6rem;}
.sm-dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#A0ADC2;margin:0 4px;opacity:.55;}
.sm-dot.on{background:#394E6E;opacity:1;}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(s):
    return _html.escape(str(s))


def html(s):
    """Render HTML safely inside Streamlit markdown (strips indentation so it is not parsed as code)."""
    st.markdown("\n".join(line.strip() for line in s.splitlines() if line.strip()), unsafe_allow_html=True)


def page_header(title, subtitle, script=None):
    parts = ""
    if script:
        parts += f'<div class="sm-script">{esc(script)}</div>'
    parts += f"<h1>{esc(title)}</h1><div class='sm-sub'>{esc(subtitle)}</div>"
    html(parts)


def stat_card(value, label):
    return f'<div class="sm-card"><div class="sm-stat-n">{esc(value)}</div><div class="sm-stat-l">{esc(label)}</div></div>'


def empty_state(title, text):
    html(f'<div class="sm-card"><div class="sm-act-t">{esc(title)}</div><div class="sm-act-d">{esc(text)}</div></div>')
