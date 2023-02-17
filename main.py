import streamlit as st
import pandas as pd
import plotly.express as px

file_saved = st.file_uploader("Upload file :sunglasses: :")

if not file_saved:
    st.info("Awaiting results file!")
# url = r"C:\Users\Akbor\Downloads\Exported_Data.xlsx"
if file_saved:
    df = pd.read_excel(file_saved)
    "# Data", df
    color_map = {
        'TAMRA':'#a8328d',
        'JOE': '#00ad3d',
        'FAM': '#006ead',
        'AR101': '#ad0026', 
        'CY5': '#4e0352',
        'CY5.5': '#521603',
        'A550': '#141413',
        'A680': '#141413',
        'HEX': '#071952',
        'A647N': '#515751'
        }
    well_names = df['well_pos'].unique()
    target_names = df['target'].unique()
    # print(target_names)

    well_selector = st.multiselect("Wells", well_names)
    target_selected = st.multiselect("Channel", target_names)
    def plot_figure(second_selection_df):
        fig = px.line(data_frame=second_selection_df, x='cycle', y='drn', line_group='well_pos', color='target', color_discrete_map=color_map)
        fig.update_layout(xaxis_title='Cycle', yaxis_title='RFU', legend_title_text='')
        fig.update_layout(xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
                )
        fig.update_layout(legend=dict(x=0.5, y=-0.2, xanchor='center', yanchor='top'))
        fig.update_layout(legend_orientation='h')
        return fig

    if well_selector or target_selected:
        if not target_selected:
            first_df = df[df["well_pos"].isin(well_selector)]
            a = plot_figure(first_df)
            a
        if target_selected and not well_selector:
            st.info("please select a well!")
        # print(target_selected)
        if target_selected and well_selector:
            second_selection_df = df[(df["target"].isin(target_selected)) & (df["well_pos"].isin(well_selector))]
            a =plot_figure(second_selection_df)
            a