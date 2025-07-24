import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from api_utils import fetch_leads_data

# Microsoft color theme
MICROSOFT_BLUE = "#0078D4"
MICROSOFT_LIGHT = "#F3F2F1"
MICROSOFT_DARK = "#201F1E"

STATUS_OPTIONS = ["InProgress", "Declined", "Opportunity Created"]


def set_page_style():
    st.set_page_config(
        page_title="Leads Dashboard",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {MICROSOFT_LIGHT};
        }}
        .css-1d391kg, .css-1v0mbdj {{
            color: {MICROSOFT_DARK};
        }}
        .css-18e3th9 {{
            background: {MICROSOFT_BLUE};
            color: white;
        }}
        .ag-theme-streamlit .ag-header, .ag-theme-streamlit .ag-root-wrapper {{
            background: {MICROSOFT_BLUE} !important;
            color: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_grid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column(
        "Status",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": STATUS_OPTIONS},
        cellStyle={"color": MICROSOFT_DARK, "backgroundColor": MICROSOFT_LIGHT},
    )
    gb.configure_default_column(editable=False, filter=True, resizable=True)
    gb.configure_grid_options(domLayout='autoHeight')
    grid_options = gb.build()

    st.markdown("#### Leads Table")
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        theme='streamlit',
        allow_unsafe_jscode=True,
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        height=400,
    )
    return grid_response['data']


@st.cache_data(show_spinner=False)
def get_data():
    data = fetch_leads_data()
    if isinstance(data, dict) and data.get("error"):
        st.error(f"Failed to fetch data: {data['error']}")
        return []
    return data


def main():
    set_page_style()
    st.title("💼 Microsoft Leads Dashboard")
    data = get_data()

    if not data:
        st.warning("No data available.")
        return

    df = pd.DataFrame(data)
    edited_df = render_grid(df)

    if not edited_df.equals(df):
        st.success("Status updated! (Note: This does not persist to the backend API)")
        st.dataframe(edited_df)
    else:
        st.caption("Edit the 'Status' column directly in the table above.")


if __name__ == "__main__":
    main() 