import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="QuantStudio Analysis", page_icon=":smile:", layout="wide", initial_sidebar_state="auto")
file_saved = st.file_uploader("Upload file :sleeping: :", accept_multiple_files=False)

if file_saved:
    df = pd.read_excel(file_saved, skiprows=23, sheet_name="Amplification Data", engine="openpyxl")
    df2 = pd.read_excel(file_saved, sheet_name="Amplification Data", nrows=22, header=None, engine="openpyxl", names=["names", "values"])
    col1, col2 = st.columns(2)
    with col1:
        f"### Imported data", df
    with col2:
        f"### File Info", df2
    color_map = {
        'TAMRA':'#a8328d',
        'JOE': '#00ad3d',
        'FAM': '#006ead',
        'AR101': '#ad0026', 
        'CY5': '#0510eb',
        'CY5.5': '#eb7405',
        'A550': '#3fb518',
        'A680': '#e30bd8',
        'HEX': '#053ef2',
        'A647N': '#515751',
        'A647': '#515751'
        }
    well_names = df['Well Position'].unique()
    target_names = df['Target'].unique()
    # print(target_names)
    well_selector = st.multiselect("Wells", well_names)
    target_selected = st.multiselect("Channel", target_names)

    def plot_figure(second_selection_df):
        fig = px.line(data_frame=second_selection_df, x='Cycle Number', y='dRn', line_group='Well Position', color='Target', color_discrete_map=color_map)
        fig.update_layout(xaxis_title='Cycle', yaxis_title='RFU', legend_title_text='')
        fig.update_layout(xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
                )
        fig.update_layout(legend=dict(x=0.5, y=-0.32, xanchor='center', yanchor='top'))
        fig.update_layout(legend_orientation='h', font=dict(family="arial", size=18,color="black"))
        fig.update_layout(autosize=False, width=800, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(title_font_family="arial", color="black")
        fig.update_yaxes(title_font_family="arial", color="black")
        # Save the plot as SVG
        fig.write_image("temp.svg", format="svg")
        with open("temp.svg", "rb") as image:
            image_binary = image.read()
        b64 = base64.b64encode(image_binary).decode("utf-8")
        download_url = f'data:image/svg+xml;base64,{b64}'
        # Display the plot
        st.plotly_chart(fig, theme=None, use_container_width=False)
        st.markdown(f'<a href="{download_url}" download="plot.svg">Download Plot as SVG</a>', unsafe_allow_html=True)
        return fig
    
    st.info("If you want to display all the filter data for give well. Only select from wells menu")

    if well_selector or target_selected:
        if not target_selected:
            first_df = df[df["Well Position"].isin(well_selector)]
            a = plot_figure(first_df)
          
        if not well_selector:
            st.info("please select a well!")
        # print(target_selected)
        if target_selected and well_selector:
            second_selection_df = df[(df["Target"].isin(target_selected)) & (df["Well Position"].isin(well_selector))]
#             a =plot_figure(second_selection_df)
            # st.plotly_chart(a, theme=None, use_container_width=False)

else:
    st.info("Awaiting results file")
