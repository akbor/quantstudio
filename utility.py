import plotly.express as px
import pandas as pd
import fileinput


def handleMissingCycles(file):
    line = open(file=file, mode='r').readlines()[0].split("\t")
    header_head = []
    for i in line:
        header_head.append(i.rstrip())
        
    
    actual_lenght = None
    
    with open(file=file,mode='r') as handle:
        for line in handle.readlines():
            if line.split("\t").__len__()>7:
                actual_lenght = line.split("\t").__len__()
                break
    cycles = [str(i) for i in range(1, actual_lenght - 6)] # -6 because there are 7 headers at first before cycles. Range is excuslive of last value
    ret = header_head + cycles
    ret [-1] = ret[-1] + "\n"
    headerLine = "\t".join(ret)
    
    with fileinput.FileInput(files=file, inplace=True) as f:
        for line in f:
            if f.isfirstline():
                print(headerLine, end="")
            else:
                print(line, end="")
    
    return

def well_position_by_index(index, well_format):
    """
    Returns the well position based on Zero-based Index
    """
    match well_format:
        case '384W':
            return f'{chr(ord("A") + int(index / 24))}{index % 24 + 1}'
        case '96W':
            return f'{chr(ord("A") + int(index / 12))}{index % 12 + 1}'
        case _:
            raise ValueError("Wrong Well Format")

def positive_ntc_group(row):
    if row.lower().startswith("negative"):
        return "Negatives"
    elif row.lower().startswith("pc") or row.lower().startswith("positive"):
        return "Positives"
    elif row.lower().startswith("npc"):
        return "NPCs"
    elif row.lower().startswith("ntc"):
        return "NTCs"
    else:
        return row
    
def plot_figure(second_selection_df):
    fig = px.line(
        data_frame=second_selection_df,
        x="Cycle Number",
        y="dRn",
        line_group="Well Position",
        color="Target",
    )
    fig.update_layout(
        xaxis_title="Cycle", yaxis_title="RFU", legend_title_text=""
    )
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.update_layout(
        legend=dict(x=0.5, y=-0.32, xanchor="center", yanchor="top")
    )
    fig.update_layout(
        legend_orientation="h",
        font=dict(family="arial", size=18, color="black"),
    )
    fig.update_layout(
        autosize=False,
        width=800,
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title_font_family="arial", color="black")
    fig.update_yaxes(title_font_family="arial", color="black")

    # Save the plot as SVG
    # fig.write_image("temp.svg", format="svg")
    # with open("temp.svg", "rb") as image:
    #     image_binary = image.read()
    # b64 = base64.b64encode(image_binary).decode("utf-8")
    # download_url = f'data:image/svg+xml;base64,{b64}'
    # # Display the plot
    # st.plotly_chart(fig, theme=None, use_container_width=False)
    # st.markdown(f'<a href="{download_url}" download="plot.svg">Download Plot as SVG</a>', unsafe_allow_html=True)
    return fig

def plot_figure2(DataFrame, colormappings, group_title):
    try:
        target_thresholds = (
            DataFrame.groupby("Target")["Threshold"].unique().apply(list).to_dict()
        )
    except KeyError:
        target_thresholds =None
    group_list = DataFrame[group_title].unique()
    fig = px.line(
        data_frame=DataFrame,
        x="Cycle Number",
        y="dRn",
        line_group="Well Position",
        color="Target",
        color_discrete_map=colormappings,
    )
    fig.update_layout(
        xaxis_title="Cycle", yaxis_title="RFU", legend_title_text=""
    )
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.update_layout(
        legend=dict(x=0.5, y=-0.2, xanchor="center", yanchor="top")
    )
    fig.update_layout(
        legend_orientation="h",
        font=dict(family="arial", size=18, color="black"),
    )
    fig.update_layout(
        autosize=False,
        width=800,
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title_font_family="arial", color="black")
    fig.update_yaxes(title_font_family="arial", color="black")
    fig.update_traces(line={"width": 1})
    if target_thresholds:
        for target, threshold in target_thresholds.items():
            fig.add_hline(
                y=threshold[0],
                line_color=colormappings.get(target),
                line_width=1,
                annotation_text=f"{threshold[0]: .2f}",
                annotation_position="top left",
                annotation_font_size=12,
                annotation_font_color="#ffffff",
                annotation=dict(
                    x=0.05,
                    xref="paper",
                    y=threshold[0],
                    yref="y",
                    showarrow=False,
                    text=f"{threshold[0]}",
                    bgcolor=colormappings.get(target),
                    bordercolor=colormappings.get(target),
                    borderwidth=1,
                    opacity=0.8,
                ),
            )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=False,
        ticks="outside",
        tickwidth=1,
        ticklen=10,
        tickcolor="black",
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=False,
        ticks="outside",
        tickwidth=1,
        ticklen=10,
        tickcolor="black",
    )
    if group_list:
        fig.update_layout(
            title= dict(
                text=f"{', '.join(group_list)}",
                x=0.5,
                xanchor="center",
                yanchor="bottom"
            )
        )

    return fig

def plot_figure3(DataFrame, colormappings, title_list):
    try:
        target_thresholds = (
            DataFrame.groupby("Target")["Threshold"].unique().apply(list).to_dict()
        )
    except KeyError:
        target_thresholds =None
    fig = px.line(
        data_frame=DataFrame,
        x="Cycle Number",
        y="dRn",
        line_group="Well Position",
        color="Target",
        color_discrete_map=colormappings,
    )
    fig.update_layout(
        xaxis_title="Cycle", yaxis_title="RFU", legend_title_text=""
    )
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.update_layout(
        legend=dict(x=0.5, y=-0.2, xanchor="center", yanchor="top")
    )
    fig.update_layout(
        legend_orientation="h",
        font=dict(family="arial", size=18, color="black"),
    )
    fig.update_layout(
        autosize=False,
        width=800,
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(title_font_family="arial", color="black")
    fig.update_yaxes(title_font_family="arial", color="black")
    fig.update_traces(line={"width": 1})
    if target_thresholds:
        for target, threshold in target_thresholds.items():
            fig.add_hline(
                y=threshold[0],
                line_color=colormappings.get(target),
                line_width=1,
                annotation_text=f"{threshold[0]: .2f}",
                annotation_position="top left",
                annotation_font_size=12,
                annotation_font_color="#ffffff",
                annotation=dict(
                    x=0.05,
                    xref="paper",
                    y=threshold[0],
                    yref="y",
                    showarrow=False,
                    text=f"{threshold[0]}",
                    bgcolor=colormappings.get(target),
                    bordercolor=colormappings.get(target),
                    borderwidth=1,
                    opacity=0.8,
                ),
            )
    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=False,
        ticks="outside",
        tickwidth=1,
        ticklen=10,
        tickcolor="black",
    )
    fig.update_yaxes(
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=False,
        ticks="outside",
        tickwidth=1,
        ticklen=10,
        tickcolor="black",
    )
    if title_list:
        fig.update_layout(
            title= dict(
                text=f"{', '.join(title_list)}",
                x=0.5,
                xanchor="center",
                yanchor="bottom"
            )
        )

    return fig