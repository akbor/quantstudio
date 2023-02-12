import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
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
    fig = px.line(data_frame=second_selection_df, x='cycle', y='drn', line_group='well_pos', color='target')
    fig.update_layout(xaxis_title='Cycle', yaxis_title='RFU', legend_title_text='')
    fig.update_layout(xaxis=dict(showgrid=False),
              yaxis=dict(showgrid=False)
              )
    fig.update_layout(
    legend=dict(x=0.5, y=-0.2, xanchor='center', yanchor='top'))
    fig