import streamlit as st
import pandas as pd
import re
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import sqlite3
import bcrypt
import base64

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="GST Reconciliation System",
    layout="wide"
)

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# -----------------------------------
# CREATE TABLE
# -----------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS reconciliation_reports (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gstin TEXT,
    invoice_no TEXT,
    pr_total_tax REAL,
    g2b_total_tax REAL,
    match_status TEXT,
    tax_difference REAL,
    tax_status TEXT,
    mismatch_reason TEXT,
    risk_level TEXT,
    duplicate_flag TEXT
)
""")

conn.commit()

# -----------------------------------
# USER TABLE
# -----------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()

# -----------------------------------
# CREATE DEFAULT USER
# -----------------------------------

default_username = "admin"
default_password = "admin123"

hashed_password = bcrypt.hashpw(
    default_password.encode(),
    bcrypt.gensalt()
)

cursor.execute(
    "SELECT * FROM users WHERE username=?",
    (default_username,)
)

existing_user = cursor.fetchone()

if not existing_user:

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (
            default_username,
            hashed_password
        )
    )

    conn.commit()

# -----------------------------------
# BACKGROUND IMAGE
# -----------------------------------

def get_base64(file):

    with open(file, "rb") as f:
        data = f.read()

    return base64.b64encode(data).decode()

bg_image = get_base64("Gst_Logo.png")
# -----------------------------------
# CUSTOM CSS
# -----------------------------------
# =====================================================
# PREMIUM CSS UI
# =====================================================

st.markdown(f"""

<style>

/* ========================================= */
/* MAIN BACKGROUND */
/* ========================================= */

[data-testid="stAppViewContainer"]{{

    background-image:

    linear-gradient(
        rgba(2,6,23,0.82),
        rgba(15,23,42,0.90)
    ),

    url("data:image/jpg;base64,{bg_image}");

    background-size: cover;

    background-position: center;

    background-repeat: no-repeat;

    background-attachment: fixed;

    color:white;
}}

/* ========================================= */
/* MAIN APP */
/* ========================================= */

.stApp{{
    background: transparent;
}}

/* ========================================= */
/* SIDEBAR */
/* ========================================= */

[data-testid="stFileUploader"]{{

    background: rgba(15,23,42,0.55) !important;

    border:1px solid rgba(255,255,255,0.08) !important;

    border-radius:22px !important;

    padding:18px !important;

    backdrop-filter: blur(12px);

    box-shadow:
    0 0 15px rgba(0,0,0,0.15);
}}

/* INNER DROPZONE */

[data-testid="stFileUploaderDropzone"]{{

    background: rgba(255,255,255,0.04) !important;

    border:2px dashed rgba(255,255,255,0.12) !important;

    border-radius:18px !important;
}}

/* DROPZONE TEXT */

[data-testid="stFileUploaderDropzone"]*{{

    color:#e2e8f0 !important;
}}

/* ========================================= */
/* REMOVE HEADER */
/* ========================================= */

header{{
    background: transparent !important;
}}

/* ========================================= */
/* FULL SIDEBAR DARK FIX */
/* ========================================= */

section[data-testid="stSidebar"]{{

    background:

    linear-gradient(
        180deg,
        rgba(2,6,23,0.96),
        rgba(15,23,42,0.96)
    ) !important;
}}

/* SIDEBAR CONTENT */

section[data-testid="stSidebar"] > div{{

    background: transparent !important;
}}

/* SIDEBAR TEXT */

section[data-testid="stSidebar"] *{{

    color:white !important;
}}

/* REMOVE WHITE BLOCK */

.css-1d391kg,
.css-163ttbj,
.css-1wrcr25{{

    background: transparent !important;
}}

/* ========================================= */
/* MAIN PADDING */
/* ========================================= */

.block-container{{
    padding-top:1rem !important;
}}

/* ========================================= */
/* TEXT */
/* ========================================= */

h1,h2,h3,h4,h5,h6{{

    color:#ffffff !important;

    font-weight:700 !important;

    text-shadow:
    0 0 10px rgba(255,255,255,0.15);
}}

p,label,span{{
    color:#e2e8f0 !important;
}}

/* ========================================= */
/* KPI GLASS CARDS */
/* ========================================= */

[data-testid="metric-container"]{{

    background: rgba(15,23,42,0.72) !important;

    backdrop-filter: blur(14px);

    border:1px solid rgba(255,255,255,0.08) !important;

    border-radius:24px !important;

    padding:22px !important;

    box-shadow:
    0 0 30px rgba(0,0,0,0.25);

    transition:0.3s;
}}

/* KPI HOVER */

[data-testid="metric-container"]:hover{{

    transform:translateY(-6px);

    box-shadow:
    0 0 12px rgba(59,130,246,0.4),
    0 0 30px rgba(59,130,246,0.3);
}}

/* KPI LABEL */

[data-testid="metric-container"] label{{

    color:#cbd5e1 !important;

    font-size:16px !important;
}}

/* KPI VALUE */

[data-testid="metric-container"] [data-testid="stMetricValue"]{{

    color:white !important;

    font-size:46px !important;

    font-weight:700 !important;
}}

/* ========================================= */
/* DATAFRAME */
/* ========================================= */

[data-testid="stDataFrame"]{{

    background: rgba(15,23,42,0.90) !important;

    border-radius:20px !important;

    overflow:hidden !important;

    border:1px solid rgba(255,255,255,0.08) !important;
}}

[data-testid="stDataFrame"] *{{
    color:white !important;
}}

[data-testid="stDataFrame"] thead tr th{{

    background:#1e3a8a !important;

    color:white !important;
}}

[data-testid="stDataFrame"] tbody tr td{{

    background: rgba(15,23,42,0.88) !important;

    color:white !important;

    border-color: rgba(255,255,255,0.05) !important;
}}

[data-testid="stDataFrame"] tbody tr:hover td{{

    background: rgba(37,99,235,0.22) !important;
}}

/* ========================================= */
/* BUTTONS */
/* ========================================= */

.stButton button,
.stDownloadButton button{{

    background:#2563eb !important;

    color:white !important;

    border:none !important;

    border-radius:12px !important;

    padding:10px 20px !important;

    font-weight:bold !important;
}}

/* ========================================= */
/* INPUTS */
/* ========================================= */

.stTextInput input{{

    background:#1e293b !important;

    color:white !important;

    border-radius:10px !important;
}}

/* ========================================= */
/* FILE UPLOADER */
/* ========================================= */

[data-testid="stFileUploader"]{{

    background: rgba(255,255,255,0.05);

    border-radius:15px;

    padding:15px;
}}

/* ========================================= */
/* SUCCESS */
/* ========================================= */

.stSuccess{{
    border-radius:15px;
}}

/* ========================================= */
/* TABS */
/* ========================================= */

.stTabs [role="tab"]{{
    color:white !important;
}}

/* ========================================= */
/* SCROLLBAR */
/* ========================================= */

::-webkit-scrollbar{{
    width:10px;
}}

::-webkit-scrollbar-thumb{{

    background:#334155;

    border-radius:10px;
}}

/* ========================================= */
/* ANIMATED GLOW */
/* ========================================= */

[data-testid="stAppViewContainer"]::before{{

    content:"";

    position:fixed;

    top:-180px;
    left:-180px;

    width:500px;
    height:500px;

    background:

    radial-gradient(

        circle,

        rgba(59,130,246,0.22),

        transparent 70%
    );

    animation: glowMove 8s infinite alternate;

    z-index:-1;
}}

[data-testid="stAppViewContainer"]::after{{

    content:"";

    position:fixed;

    bottom:-200px;
    right:-200px;

    width:550px;
    height:550px;

    background:

    radial-gradient(

        circle,

        rgba(14,165,233,0.18),

        transparent 70%
    );

    animation: glowMove2 10s infinite alternate;

    z-index:-1;
}}

/* ========================================= */
/* ANIMATION */
/* ========================================= */

@keyframes glowMove{{

    from{{
        transform:translate(0px,0px);
    }}

    to{{
        transform:translate(120px,80px);
    }}
}}

@keyframes glowMove2{{

    from{{
        transform:translate(0px,0px);
    }}

    to{{
        transform:translate(-100px,-60px);
    }}
}}

</style>

""", unsafe_allow_html=True)
# -----------------------------------
# NORMALIZE COLUMN
# -----------------------------------

def normalize_column(col):

    col = str(col).strip().lower()
    col = re.sub(r'[^a-z0-9]', '', col)

    return col

# -----------------------------------
# STANDARD COLUMN MAPPING
# -----------------------------------

STANDARD_COLUMNS = {

    "gstin": [
        "gstin",
        "suppliergstin",
        "vendorgstin",
        "gstinofsupplier"
    ],

    "invoice_no": [
        "invoiceno",
        "billno",
        "billno.",
        "invoicenumber",
        "documentno"
    ],

    "invoice_date": [
        "invoicedate",
        "billdate",
        "documentdate"
    ],

    "taxable_value": [
        "taxablevalue",
        "taxableamount",
        "taxablevalueofrec",
        "taxablevalueofpay"
    ],

    "igst": [
        "igstreceivable",
        "integratedtax",
        "igst"
    ],

    "cgst": [
        "cgstreceivable",
        "centraltax",
        "cgst"
    ],

    "sgst": [
        "sgstreceivable",
        "stateuttax",
        "sgst"
    ]
}

# -----------------------------------
# READ FILE FUNCTION
# -----------------------------------

def read_file(file):

    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)

# -----------------------------------
# AUTO COLUMN MAPPING
# -----------------------------------

def auto_map_columns(df):

    mapped_columns = {}

    normalized_columns = {
        normalize_column(col): col
        for col in df.columns
    }

    for standard_col, possible_names in STANDARD_COLUMNS.items():

        found = None

        for name in possible_names:

            if name in normalized_columns:
                found = normalized_columns[name]
                break

        mapped_columns[standard_col] = found

    return mapped_columns

# -----------------------------------
# EXCEL EXPORT FUNCTION
# -----------------------------------

def convert_to_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="GST_Reconciliation"
        )

    processed_data = output.getvalue()

    return processed_data

# -----------------------------------
# SAVE TO DATABASE
# -----------------------------------

def save_to_database(df):

    df_to_save = df.copy()

    df_to_save.columns = [
        "gstin",
        "invoice_no",
        "pr_total_tax",
        "g2b_total_tax",
        "match_status",
        "tax_difference",
        "tax_status",
        "mismatch_reason",
        "risk_level",
        "duplicate_flag"
    ]

    df_to_save.to_sql(
        "reconciliation_reports",
        conn,
        if_exists="append",
        index=False
    )

# -----------------------------------
# PDF REPORT FUNCTION
# -----------------------------------

def create_pdf_report(df, pr_gstin, pr_invoice):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        200,
        10,
        txt="GST Reconciliation Report",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.cell(
        200,
        10,
        txt=f"Total Invoices: {len(df)}",
        ln=True
    )

    matched = len(
        df[df["MATCH_STATUS"] == "Matched"]
    )

    missing = len(
        df[df["MATCH_STATUS"] == "Missing in GSTR2B"]
    )

    pdf.cell(
        200,
        10,
        txt=f"Matched Invoices: {matched}",
        ln=True
    )

    pdf.cell(
        200,
        10,
        txt=f"Missing Invoices: {missing}",
        ln=True
    )

    pdf.ln(10)

    pdf.set_font(
        "Arial",
        "B",
        10
    )

    pdf.cell(45, 10, "GSTIN", 1)
    pdf.cell(40, 10, "Invoice", 1)
    pdf.cell(35, 10, "Tax Diff", 1)
    pdf.cell(35, 10, "Risk", 1)

    pdf.ln()

    pdf.set_font(
        "Arial",
        size=9
    )

    for index, row in df.head(20).iterrows():

        pdf.cell(
            45,
            10,
            str(row[pr_gstin])[:20],
            1
        )

        pdf.cell(
            40,
            10,
            str(row[pr_invoice])[:18],
            1
        )

        pdf.cell(
            35,
            10,
            str(round(row["TAX_DIFFERENCE"], 2)),
            1
        )

        pdf.cell(
            35,
            10,
            str(row["RISK_LEVEL"]),
            1
        )

        pdf.ln()

    return pdf.output(dest="S").encode("latin-1")

# -----------------------------------
# SESSION STATE
# -----------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------------
# LOGIN SYSTEM
# -----------------------------------

if not st.session_state.logged_in:

    st.title("Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user:

            stored_password = user[2]

            if bcrypt.checkpw(
                password.encode(),
                stored_password
            ):

                st.session_state.logged_in = True

                st.success("Login Successful")

                st.rerun()

            else:
                st.error("Invalid Password")

        else:
            st.error("User Not Found")

    st.stop()

# -----------------------------------
# TITLE
# -----------------------------------

st.markdown("""

# GST Reconciliation System

### Smart GST Matching & ITC Verification

""")

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.header("Upload GST Files")

purchase_file = st.sidebar.file_uploader(
    "Upload Purchase Register",
    type=["xlsx", "csv"]
)

gstr2b_file = st.sidebar.file_uploader(
    "Upload GSTR2B File",
    type=["xlsx", "csv"]
)

# -----------------------------------
# LOGOUT BUTTON
# -----------------------------------

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.rerun()

# -----------------------------------
# PROCESS FILES
# -----------------------------------

if purchase_file and gstr2b_file:

    purchase_df = read_file(purchase_file)
    gstr2b_df = read_file(gstr2b_file)

    st.success("Files Uploaded Successfully")

    # -----------------------------------
    # AUTO MAPPING
    # -----------------------------------

    purchase_mapping = auto_map_columns(purchase_df)
    gstr2b_mapping = auto_map_columns(gstr2b_df)

    purchase_mapping_df = pd.DataFrame({

        "Standard Column": purchase_mapping.keys(),

        "Mapped Column": purchase_mapping.values()
    })

    gstr2b_mapping_df = pd.DataFrame({

        "Standard Column": gstr2b_mapping.keys(),

        "Mapped Column": gstr2b_mapping.values()
    })

    # -----------------------------------
    # EXTRACT STANDARD COLUMNS
    # -----------------------------------

    pr_gstin = purchase_mapping["gstin"]
    pr_invoice = purchase_mapping["invoice_no"]

    g2b_gstin = gstr2b_mapping["gstin"]
    g2b_invoice = gstr2b_mapping["invoice_no"]

    # -----------------------------------
    # TAX COLUMNS
    # -----------------------------------

    pr_igst = purchase_mapping["igst"]
    pr_cgst = purchase_mapping["cgst"]
    pr_sgst = purchase_mapping["sgst"]

    g2b_igst = gstr2b_mapping["igst"]
    g2b_cgst = gstr2b_mapping["cgst"]
    g2b_sgst = gstr2b_mapping["sgst"]

    # -----------------------------------
    # PURCHASE TOTAL TAX
    # -----------------------------------

    purchase_df["PR_TOTAL_TAX"] = (

        pd.to_numeric(
            purchase_df[pr_igst],
            errors="coerce"
        ).fillna(0)

        +

        pd.to_numeric(
            purchase_df[pr_cgst],
            errors="coerce"
        ).fillna(0)

        +

        pd.to_numeric(
            purchase_df[pr_sgst],
            errors="coerce"
        ).fillna(0)
    )

    # -----------------------------------
    # GROUP PURCHASE DATA
    # -----------------------------------

    purchase_df = purchase_df.groupby(
        [
            pr_gstin,
            pr_invoice
        ],
        as_index=False
    ).agg({
        "PR_TOTAL_TAX": "sum"
    })

    # -----------------------------------
    # GSTR2B TOTAL TAX
    # -----------------------------------

    gstr2b_df["G2B_TOTAL_TAX"] = (

        pd.to_numeric(
            gstr2b_df[g2b_igst],
            errors="coerce"
        ).fillna(0)

        +

        pd.to_numeric(
            gstr2b_df[g2b_cgst],
            errors="coerce"
        ).fillna(0)

        +

        pd.to_numeric(
            gstr2b_df[g2b_sgst],
            errors="coerce"
        ).fillna(0)
    )

    # -----------------------------------
    # GROUP GSTR2B DATA
    # -----------------------------------

    gstr2b_df = gstr2b_df.groupby(
        [
            g2b_gstin,
            g2b_invoice
        ],
        as_index=False
    ).agg({
        "G2B_TOTAL_TAX": "sum"
    })

    # -----------------------------------
    # CREATE MATCH KEYS
    # -----------------------------------

    purchase_df["MATCH_KEY"] = (
        purchase_df[pr_gstin].astype(str).str.strip()
        + "_"
        + purchase_df[pr_invoice].astype(str).str.strip()
    )

    gstr2b_df["MATCH_KEY"] = (
        gstr2b_df[g2b_gstin].astype(str).str.strip()
        + "_"
        + gstr2b_df[g2b_invoice].astype(str).str.strip()
    )

    # -----------------------------------
    # MERGE DATA
    # -----------------------------------

    filtered_df = purchase_df.merge(
        gstr2b_df[["MATCH_KEY", "G2B_TOTAL_TAX"]],
        on="MATCH_KEY",
        how="left"
    )

    # -----------------------------------
    # MATCH STATUS
    # -----------------------------------

    filtered_df["MATCH_STATUS"] = filtered_df[
        "MATCH_KEY"
    ].isin(
        gstr2b_df["MATCH_KEY"]
    )

    filtered_df["MATCH_STATUS"] = filtered_df[
        "MATCH_STATUS"
    ].map({
        True: "Matched",
        False: "Missing in GSTR2B"
    })

    # -----------------------------------
    # TAX DIFFERENCE
    # -----------------------------------

    filtered_df["G2B_TOTAL_TAX"] = filtered_df[
        "G2B_TOTAL_TAX"
    ].fillna(0)

    filtered_df["TAX_DIFFERENCE"] = (
        filtered_df["PR_TOTAL_TAX"]
        -
        filtered_df["G2B_TOTAL_TAX"]
    )

    # -----------------------------------
    # TAX MATCH STATUS
    # -----------------------------------

    def tax_status(diff):

        if diff == 0:
            return "Tax Matched"

        elif diff > 0:
            return "Excess ITC Claimed"

        else:
            return "Short ITC Claimed"

    filtered_df["TAX_STATUS"] = filtered_df[
        "TAX_DIFFERENCE"
    ].apply(tax_status)

    # -----------------------------------
    # MISMATCH REASON
    # -----------------------------------

    def mismatch_reason(row):

        if row["MATCH_STATUS"] == "Missing in GSTR2B":
            return "Invoice Missing in GSTR2B"

        elif row["TAX_STATUS"] == "Excess ITC Claimed":
            return "Purchase Tax Greater than GSTR2B"

        elif row["TAX_STATUS"] == "Short ITC Claimed":
            return "Purchase Tax Less than GSTR2B"

        else:
            return "Fully Matched"

    filtered_df["MISMATCH_REASON"] = filtered_df.apply(
        mismatch_reason,
        axis=1
    )

    # -----------------------------------
    # RISK LEVEL
    # -----------------------------------

    def risk_level(row):

        if row["MATCH_STATUS"] == "Missing in GSTR2B":
            return "High"

        elif abs(row["TAX_DIFFERENCE"]) > 1000:
            return "Medium"

        else:
            return "Low"

    filtered_df["RISK_LEVEL"] = filtered_df.apply(
        risk_level,
        axis=1
    )

    # -----------------------------------
    # DUPLICATE INVOICE DETECTION
    # -----------------------------------

    filtered_df["DUPLICATE_FLAG"] = filtered_df.duplicated(
        subset=[
            pr_gstin,
            pr_invoice
        ],
        keep=False
    )

    filtered_df["DUPLICATE_FLAG"] = filtered_df[
        "DUPLICATE_FLAG"
    ].map({
        True: "Duplicate Invoice",
        False: "Unique Invoice"
    })

    # -----------------------------------
    # SIDEBAR FILTERS
    # -----------------------------------

    st.sidebar.header("Filters")

    match_filter = st.sidebar.multiselect(
        "Match Status",
        options=filtered_df["MATCH_STATUS"].unique(),
        default=filtered_df["MATCH_STATUS"].unique()
    )

    risk_filter = st.sidebar.multiselect(
        "Risk Level",
        options=filtered_df["RISK_LEVEL"].unique(),
        default=filtered_df["RISK_LEVEL"].unique()
    )

    # -----------------------------------
    # SEARCH FILTERS
    # -----------------------------------

    invoice_search = st.sidebar.text_input(
        "Search Invoice Number"
    )

    gstin_search = st.sidebar.text_input(
        "Search GSTIN"
    )
    # -----------------------------------
    # APPLY FILTERS
    # -----------------------------------

    filtered_df = filtered_df[
        (
            filtered_df["MATCH_STATUS"].isin(match_filter)
        )
        &
        (
            filtered_df["RISK_LEVEL"].isin(risk_filter)
        )
    ]

        # Invoice Search

    if invoice_search:
        filtered_df = filtered_df[
            filtered_df[pr_invoice]
            .astype(str)
            .str.contains(
                invoice_search,
                case=False,
                na=False
            )
        ]
    # GSTIN Search

    if gstin_search:

        filtered_df = filtered_df[
            filtered_df[pr_gstin]
            .astype(str)
            .str.contains(
                gstin_search,
                case=False,
                na=False
            )
        ]

    # GSTIN Search
    if gstin_search:

        filtered_df = filtered_df[
            filtered_df[pr_gstin]
            .astype(str)
            .str.contains(
                gstin_search,
                case=False,
                na=False
            )
        ]

    # -----------------------------------
    # KPI CALCULATIONS
    # -----------------------------------

    total_invoices = len(filtered_df)

    matched_count = len(
        filtered_df[
            filtered_df["MATCH_STATUS"] == "Matched"
        ]
    )

    missing_count = len(
        filtered_df[
            filtered_df["MATCH_STATUS"] == "Missing in GSTR2B"
        ]
    )

    duplicate_count = len(
        filtered_df[
            filtered_df["DUPLICATE_FLAG"] == "Duplicate Invoice"
        ]
    )

    high_risk_count = len(
        filtered_df[
            filtered_df["RISK_LEVEL"] == "High"
        ]
    )

    # -----------------------------------
    # KPI DASHBOARD
    # -----------------------------------

    st.subheader("GST Reconciliation Dashboard")

    st.markdown("""
    <style>

    [data-testid="metric-container"]{
        border-left: 5px solid #38bdf8;
        transition: 0.3s;
    }

    [data-testid="metric-container"]:hover{
        transform: scale(1.05);
        box-shadow:0 0 25px rgba(56,189,248,0.5);
    }

    </style>
    """, unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.metric("Total Invoices", total_invoices)

    with kpi2:
        st.metric("Matched", matched_count)

    with kpi3:
        st.metric("Missing", missing_count)

    with kpi4:
        st.metric("Duplicate", duplicate_count)

    with kpi5:
        st.metric("High Risk", high_risk_count)

    # -----------------------------------
    # MATCH STATUS CHART
    # -----------------------------------

    match_chart = px.pie(
        filtered_df,
        names="MATCH_STATUS",
        title="Match Status Distribution",

        color_discrete_sequence=[
            "#38bdf8",
            "#2563eb"
        ]
    )
    match_chart.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#ffffff",
            size=18
        ),

        title_font=dict(
            size=30,
            color="#ffffff"
        ),

        legend=dict(
            font=dict(
                color="#ffffff",
                size=16
            )
        )
    )

    st.plotly_chart(
        match_chart,
        width="stretch"
    )

    # -----------------------------------
    # RISK LEVEL CHART(BAR)
    # -----------------------------------

    risk_chart = px.bar(

        filtered_df["RISK_LEVEL"]
        .value_counts()
        .reset_index(),

        x="RISK_LEVEL",

        y="count",

        title="Risk Level Analysis",

        color="RISK_LEVEL",

        color_discrete_map={

            "High":"#ef4444",
            "Medium":"#f59e0b",
            "Low":"#22c55e"
        }
    )

    # DARK THEME

    risk_chart.update_layout(

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#ffffff",
            size=18
        ),

        title_font=dict(
            size=30,
            color="#ffffff"
        ),

        xaxis=dict(
            showgrid=False,
            color="#ffffff"
        ),

        yaxis=dict(
            showgrid=False,
            color="#ffffff"
        )
    )

    st.plotly_chart(
        risk_chart,
        width="stretch"
    )

    # -----------------------------------
    # VENDOR SUMMARY
    # -----------------------------------

    st.subheader("Vendor Summary")

    vendor_summary = filtered_df.groupby(
        pr_gstin,
        as_index=False
    ).agg({
        "PR_TOTAL_TAX": "sum",
        "MATCH_STATUS": lambda x: (x == "Matched").sum(),
        "TAX_DIFFERENCE": "sum"
    })

    vendor_summary.columns = [
        "GSTIN",
        "Total Tax",
        "Matched Invoices",
        "Total Tax Difference"
    ]

    st.dataframe(
        vendor_summary,
        width = "stretch",
        height=250,
        hide_index=True
    )

    # -----------------------------------
    # VENDOR RISK SCORE
    # -----------------------------------

    vendor_summary["Risk Score"] = (
        abs(vendor_summary["Total Tax Difference"])
        / 100
    ).round(0)

    def vendor_risk(score):

        if score > 50:
            return "High Risk"

        elif score > 20:
            return "Medium Risk"

        else:
            return "Low Risk"

    vendor_summary["Vendor Risk"] = (
        vendor_summary["Risk Score"]
        .apply(vendor_risk)
    )

    st.subheader("Vendor Risk Scoring")

    st.dataframe(

        vendor_summary[
            [
                "GSTIN",
                "Total Tax",
                "Matched Invoices",
                "Total Tax Difference",
                "Risk Score",
                "Vendor Risk"
            ]
        ],
        width="stretch",
        height=250,
        hide_index=True
    )

    # -----------------------------------
    # SHOW RESULT
    # -----------------------------------

    st.subheader("GST Reconciliation Result")

    st.dataframe(

        filtered_df[
            [
                pr_gstin,
                pr_invoice,
                "PR_TOTAL_TAX",
                "G2B_TOTAL_TAX",
                "MATCH_STATUS",
                "MISMATCH_REASON",
                "RISK_LEVEL",
                "DUPLICATE_FLAG"
            ]
        ],
        width="stretch",
        height=450,
        hide_index=True
    )

    # -----------------------------------
    # PDF DOWNLOAD BUTTON
    # -----------------------------------

    pdf_data = create_pdf_report(
        filtered_df,
        pr_gstin,
        pr_invoice
    )

    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name="GST_Reconciliation_Report.pdf",
        mime="application/pdf"
    )

    # -----------------------------------
    # GENERATE EXCEL
    # -----------------------------------

    excel_data = convert_to_excel(filtered_df)

    # -----------------------------------
    # DOWNLOAD BUTTON
    # -----------------------------------

    st.download_button(
        label="Download GST Reconciliation Report",
        data=excel_data,
        file_name="GST_Reconciliation_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # -----------------------------------
    # SAVE BUTTON
    # -----------------------------------

    if st.button("Save Report to Database"):

        save_to_database(
            filtered_df[
                [
                    pr_gstin,
                    pr_invoice,
                    "PR_TOTAL_TAX",
                    "G2B_TOTAL_TAX",
                    "MATCH_STATUS",
                    "TAX_DIFFERENCE",
                    "TAX_STATUS",
                    "MISMATCH_REASON",
                    "RISK_LEVEL",
                    "DUPLICATE_FLAG"
                ]
            ]
        )

        st.success("Report Saved Successfully")

    # -----------------------------------
    # SHOW MAPPING
    # -----------------------------------

    st.subheader("Auto Column Mapping")

    col1, col2 = st.columns(2)

    with col1:

        st.write("Purchase Register Mapping")
        st.dataframe(
            purchase_mapping_df,
            width="stretch",
            height=250,
            hide_index=True
        )

    with col2:

        st.write("GSTR2B Mapping")
        st.dataframe(
            gstr2b_mapping_df,
            width="stretch",
            height=250,
            hide_index=True
        )

    # -----------------------------------
    # SHOW DATA
    # -----------------------------------

    tab1, tab2 = st.tabs(
        ["Purchase Register", "GSTR2B"]
    )

    with tab1:
        st.dataframe(
            purchase_df,
            width="stretch",
            height=250,
            hide_index=True
        )

    with tab2:
        st.dataframe(
            gstr2b_df,
            width="stretch",
            height=250,
            hide_index=True
        )

    # -----------------------------------
    # COLUMN DISPLAY
    # -----------------------------------

    st.subheader("Detected Columns")

    col1, col2 = st.columns(2)

    with col1:

        st.write("Purchase Columns")
        purchase_columns_df = pd.DataFrame({

            "Purchase Columns": list(purchase_df.columns)
        })

        st.dataframe(

            purchase_columns_df,

            width="stretch",

            height=250,

            hide_index=True
        )

    with col2:

        st.write("GSTR2B Columns")
        gstr2b_columns_df = pd.DataFrame({
            "GSTR2B Columns": list(gstr2b_df.columns)
        })

        st.dataframe(
            gstr2b_columns_df,
            width="stretch",
            height=250,
            hide_index=True
        )


st.markdown("""
<hr>

<div style='
text-align:center;
padding:20px;
font-size:18px;
color:white;
'>

Developed By <b>SANTOSH PARIHAR</b>
            
+91-7284063170
            
santoshdataanalysts@gmail.com
</div>
""", unsafe_allow_html=True)