import pandas as pd
import streamlit as st
import plotly.express as px

# Login System

USERNAME = "JINKAL"
PASSWORD = "JINKAL"

st.sidebar.title("Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input(
    "Password",
    type="password"
)

if username != USERNAME or password != PASSWORD:
    st.warning("""🌟 Welcome to the Future of GST Automation 🌟

Every expert was once a beginner.  
Every dashboard starts with raw data.  
Every success starts with one step forward.

📊 Analyze Smarter  
⚡ Reconcile Faster  
💡 Build Better Insights  

“Dream big. Start small. Stay consistent.”

🔐 Login to continue your journey
""")
    st.stop()


st.title("SANTOSH GST RECONCILIATION APP")

purchase_file = st.file_uploader(
    "Upload Purchase Register",
    type=["xlsx", "csv"]
)

gstr2b_file = st.file_uploader(
    "Upload GSTR-2B",
    type=["xlsx", "csv"]
)

if purchase_file and gstr2b_file:

    
    # Column Mapping Dictionary
    column_mapping = {
    "gstin": "Supplier GSTIN",
    "supplier gstin": "Supplier GSTIN",
    "vendor gstin": "Supplier GSTIN",
    "gst number": "Supplier GSTIN",

    "invoice no": "Invoice No",
    "invoice number": "Invoice No",
    "inv no": "Invoice No",
    "bill no": "Invoice No",

    "igst": "IGST",
    "cgst": "CGST",
    "sgst": "SGST"
    }
    # Auto Rename Function
    def standardize_columns(df):

        new_columns = {}

        for col in df.columns:

            clean_col = col.strip().lower()

        if clean_col in column_mapping:
            new_columns[col] = column_mapping[clean_col]

        df.rename(columns=new_columns, inplace=True)

        return df

    # Read Files
    purchase_df = pd.read_excel(purchase_file)
    gstr2b_df = pd.read_excel(gstr2b_file)

    # Standardize Columns
    purchase_df = standardize_columns(purchase_df)
    gstr2b_df = standardize_columns(gstr2b_df)

    # Show Data
    st.subheader("Purchase Register")
    st.dataframe(purchase_df.head())

    st.subheader("GSTR-2B")
    st.dataframe(gstr2b_df.head())

    # Column Cleaning
    purchase_df.columns = purchase_df.columns.str.strip()
    gstr2b_df.columns = gstr2b_df.columns.str.strip()

    # Clean Invoice Function

    def clean_invoice(invoice):

        return str(invoice).replace("-", "").replace(" ", "").lower()

    # Unique Key
    purchase_df["Unique_Key"] = (
        purchase_df["Supplier GSTIN"].astype(str)
        + "_"
        + purchase_df["Invoice No"].apply(clean_invoice)
    )

    gstr2b_df["Unique_Key"] = (
        gstr2b_df["Supplier GSTIN"].astype(str)
        + "_"
        + gstr2b_df["Invoice No"].apply(clean_invoice)
    )

    # Match Status
    purchase_df["Match_Status"] = purchase_df["Unique_Key"].isin(
        gstr2b_df["Unique_Key"]
    )

    purchase_df["Match_Status"] = purchase_df["Match_Status"].map({
        True: "Matched",
        False: "Missing in 2B"
    })

    # Reconciliation Result
    st.subheader("Reconciliation Result")

    st.dataframe(
        purchase_df[
            [
                "Supplier GSTIN",
                "Invoice No",
                "Match_Status"
            ]
        ]
    )

    # Merge
    filtered_df = pd.merge(
        purchase_df,
        gstr2b_df,
        on="Unique_Key",
        how="left",
        suffixes=("_PR", "_2B")
    )

    # Safe Function
    def get_column(df, col_name):
        if col_name in df.columns:
            return pd.to_numeric(
                df[col_name],
                errors="coerce"
            ).fillna(0)
        else:
            return 0

    # Purchase Tax
    filtered_df["PR_Total_Tax"] = (
        get_column(filtered_df, "IGST_PR")
        + get_column(filtered_df, "CGST_PR")
        + get_column(filtered_df, "SGST_PR")
    )

    # 2B Tax
    filtered_df["2B_Total_Tax"] = (
        get_column(filtered_df, "IGST_2B")
        + get_column(filtered_df, "CGST_2B")
        + get_column(filtered_df, "SGST_2B")
    )

    # Tax Status
    filtered_df["Tax_Status"] = filtered_df.apply(
        lambda row:
        "Tax Matched"
        if row["PR_Total_Tax"] == row["2B_Total_Tax"]
        else "Tax Mismatch",
        axis=1
    )
    # Mismatch Reason

    def get_reason(row):

        if row["Match_Status"] == "Missing in 2B":
            return "Supplier Not Uploaded"

        elif row["PR_Total_Tax"] > row["2B_Total_Tax"]:
            return "Excess ITC Claimed"

        elif row["PR_Total_Tax"] < row["2B_Total_Tax"]:
            return "2B Tax Higher"

        else:
            return "Matched"


    filtered_df["Mismatch_Reason"] = filtered_df.apply(
        get_reason,
        axis=1
)
    
    # Risk Level

    def get_risk_level(row):

        difference = abs(
            row["PR_Total_Tax"]
            - row["2B_Total_Tax"]
    )

        if row["Match_Status"] == "Missing in 2B":
            return "High Risk"

        elif difference > 5000:
            return "High Risk"

        elif difference > 1000:
            return "Medium Risk"

        else:
            return "Low Risk"


    filtered_df["Risk_Level"] = filtered_df.apply(
        get_risk_level,
        axis=1
    )
    # Sidebar Filters
    st.sidebar.header("Filters")

    vendor_filter = st.sidebar.multiselect(
        "Select Vendor GSTIN",
        filtered_df["Supplier GSTIN_PR"].unique()
    )

    tax_filter = st.sidebar.multiselect(
        "Select Tax Status",
        filtered_df["Tax_Status"].unique()
    )

    # Apply Filters
    if vendor_filter:
        filtered_df = filtered_df[
            filtered_df["Supplier GSTIN_PR"].isin(vendor_filter)
        ]

    if tax_filter:
        filtered_df = filtered_df[
            filtered_df["Tax_Status"].isin(tax_filter)
        ]

    # KPI
    total_invoices = len(filtered_df)

    matched_count = len(
        filtered_df[
            filtered_df["Tax_Status"] == "Tax Matched"
        ]
    )

    mismatch_count = len(
        filtered_df[
            filtered_df["Tax_Status"] == "Tax Mismatch"
        ]
    )

    match_percent = round(
        (matched_count / total_invoices) * 100,
        2
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total", total_invoices)
    col2.metric("Matched", matched_count)
    col3.metric("Mismatch", mismatch_count)
    col4.metric("Match %", f"{match_percent}%")

    # Final Table
    st.subheader("Final Reconciliation")

    st.dataframe(
        filtered_df[
            [
                "Supplier GSTIN_PR",
                "Invoice No_PR",
                "PR_Total_Tax",
                "2B_Total_Tax",
                "Tax_Status",
                "Match_Status",
                "Mismatch_Reason",
                "Risk_Level"
            ]
        ]
    )

    # Duplicate
    duplicate_df = purchase_df[
        purchase_df.duplicated(
            subset=[
                "Supplier GSTIN",
                "Invoice No"
            ],
            keep=False
        )
    ]

    st.subheader("Duplicate Invoices")
    st.dataframe(duplicate_df)

    # Excess ITC
    excess_itc_df = filtered_df[
        filtered_df["PR_Total_Tax"]
        >
        filtered_df["2B_Total_Tax"]
    ]

    st.subheader("Excess ITC Cases")

    st.dataframe(
        excess_itc_df[
            [
                "Invoice No_PR",
                "PR_Total_Tax",
                "2B_Total_Tax",
                "Tax_Status"
            ]
        ]
    )
    # Missing Invoices

    missing_df = filtered_df[
        filtered_df["Match_Status"] == "Missing in 2B"
    ]

    st.subheader("Missing Invoices")

    st.dataframe(
        missing_df[
        [
            "Supplier GSTIN_PR",
            "Invoice No_PR",
            "PR_Total_Tax",
            "Match_Status"
        ]
        ]
    )
    # Pie Chart
    status_count = filtered_df["Tax_Status"].value_counts()

    fig = px.pie(
        names=status_count.index,
        values=status_count.values,
        title="Tax Match Summary"
    )

    st.plotly_chart(fig)

    # Bar Chart
    vendor_summary = filtered_df.groupby(
        "Supplier GSTIN_PR"
    )[
        ["PR_Total_Tax", "2B_Total_Tax"]
    ].sum().reset_index()

    fig2 = px.bar(
        vendor_summary,
        x="Supplier GSTIN_PR",
        y=["PR_Total_Tax", "2B_Total_Tax"],
        barmode="group",
        title="Vendor Wise Tax Comparison"
    )

    st.plotly_chart(fig2)

    # AI Summary

    high_risk_count = len(
        filtered_df[
            filtered_df["Risk_Level"] == "High Risk"
        ]
    )

    summary_text = f"""
    Total {total_invoices} invoices processed.

    {matched_count} invoices matched successfully.

    {mismatch_count} invoices have mismatches.

    {high_risk_count} invoices are marked as High Risk.

    Please review Excess ITC and Missing Invoice cases.
    """

    st.subheader("AI Reconciliation Summary")

    st.info(summary_text)

    # Vendor Summary
    vendor_summary_df = filtered_df.groupby(
        "Supplier GSTIN_PR"
    ).agg(
        Total_Invoices=("Invoice No_PR", "count"),
        Purchase_Tax=("PR_Total_Tax", "sum"),
        GSTR2B_Tax=("2B_Total_Tax", "sum")
    ).reset_index()

    # Difference
    vendor_summary_df["Difference"] = (
        vendor_summary_df["Purchase_Tax"]
        - vendor_summary_df["GSTR2B_Tax"]
    )

    st.subheader("Vendor Summary")

    st.dataframe(vendor_summary_df)

    # Download
    output_file = "reconciliation_report.xlsx"

    filtered_df.to_excel(
        output_file,
        index=False
    )

    with open(output_file, "rb") as file:
        st.download_button(
            label="Download Reconciliation Report",
            data=file,
            file_name="GST_Reconciliation_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# AI GST Assistant

st.subheader("AI GST Assistant")

user_question = st.text_input(
    "Ask anything about reconciliation"
)
if user_question:

    question = user_question.lower()

    # Mismatch Question
    if "mismatch" in question:
        st.success(
            f"There are {mismatch_count}mismatched invoices."
        )

    # Matched Question
    elif "matched" in question:

        st.success(
            f"{matched_count} invoices matched successfully."
        )

    # High Risk Question
    elif "risk" in question:

        high_risk = len(
            filtered_df[
                filtered_df["Risk_Level"] == "High Risk"
            ]
        )

        st.success(
            f"{high_risk} invoices are High Risk."
        )

            # Missing Invoice Question
    elif "missing" in question:

            missing_count = len(
                filtered_df[
                filtered_df["Match_Status"] == "Missing in 2B"
            ]
        )

            st.success(
                f"{missing_count} invoices are missing in 2B."
        )

# Vendor Question
    elif "vendor" in question:

        vendor_summary_df = filtered_df.groupby(
            "Supplier GSTIN_PR"
        ).agg(
            Difference=(
                "PR_Total_Tax",
                "sum"
            )
        ).reset_index()

        risky_vendor = vendor_summary_df.iloc[0]

        st.success(
            f"""
            Highest mismatch vendor:
            {risky_vendor['Supplier GSTIN_PR']}
            """
        )

    else:

        st.warning(
            "Ask about mismatch, vendor, risk or missing invoices."
        )