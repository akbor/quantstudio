import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
url = r"C:\Users\Akbor\Downloads\Exported_Data.xlsx"

df = pd.read_excel(url)

"# AH225 - Results", df

well_names = df['well_pos'].unique()
target_names = df['target'].unique()
well_selector = st.multiselect("Wells", well_names)
target_selected = st.multiselect("Channel", target_names)
if well_selector or target_selected:
    print(well_selector)
    first_df = df[df["well_pos"].isin(well_selector)]
    print(target_selected)
    second_selection_df = first_df[first_df["target"].isin(target_selected)]
    second_selection_df
    plot = px.scatter(second_selection_df, x="cycle", y="drn", color="target")

    st.plotly_chart(plot)

    