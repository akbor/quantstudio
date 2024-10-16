import streamlit as st
import pandas as pd
from utility import plot_figure, plot_figure2, plot_figure3,positive_ntc_group, handleMissingCycles, well_position_by_index
import rdmlpython
import zipfile, json
run = rdmlpython.Rdml()
RDLM = False
EDS = False

st.set_page_config(
    page_title="QuantStudio Analysis",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="auto",
)
color_map = {
    "TAMRA": "#a8328d",
    "JOE": "#a40000",
    "ROX": "#a40000",
    "Texas Red": "#a40000",
    "FAM": "#1f76ba",
    "AR101": "#ad0026",
    "CY5": "#7a14a9",
    "Cy5": "#7a14a9",
    "CY5.5": "#eb7405",
    "A550": "#3fb518",
    "A680": "#e30bd8",
    "HEX": "#187b27",
    "VIC": "#187b27",
    "A647N": "#515751",
    "A647": "#515751",
}
@st.cache_data
def transform_json_to_df(wellResult, target_reporter_dict, well_format):
    "Pass in the 'wellResults' dict"
    
    records = []
    for data in wellResult:
        sampleName = data['sampleName']
        wellIndex = data['wellIndex']
        
        for result in data['reactionResults']:
            targetName = result['targetName']
            deltaRn = result['amplificationResult']['deltaRn']
            threshold = result['amplificationResult']['ctThreshold']
            cycle_numbers = list(range(1, len(deltaRn) + 1)) 
            
            for i in range(len(deltaRn)):
                records.append({
                    'wellIndex': wellIndex,
                    'Well Position': well_position_by_index(index=wellIndex, well_format=well_format),
                    'Sample': sampleName,
                    'Target': targetName,
                    'Reporter': target_reporter_dict[targetName],
                    'Threshold': threshold,
                    'dRn': deltaRn[i],
                    'Cycle Number': cycle_numbers[i]
                })
    return pd.DataFrame(records, columns=['wellIndex', 'Well Position','Sample', 'Target', 'Reporter', 'dRn', 'Cycle Number','Threshold'])
@st.cache_data
def read_rdml(l):
    return pd.concat(l)

@st.cache_data
def read_json_from_zip(zip_file_path, interested_file):
    with zipfile.ZipFile(zip_file_path, 'r') as handle:
        with handle.open(interested_file) as ret:
            return json.load(ret)
@st.cache_data
def read_rdml_file(filepath):
    try:
        df = pd.read_csv(filepath, sep="\t", header=0)
        print(f"INFO: removing - {f}.csv")
        # os.remove(f"{f}.csv")
        return df.melt(
            id_vars=df.columns[:7],
            value_vars=df.columns[7:],
            var_name="Cycle Number",
            value_name="dRn"
        ).rename(columns=
            {"Well":"Well Position",
            "Dye": "Reporter"}
        )
        # print(f"removed: {f}.csv")
    except Exception:
        print("Hanlding Mising Cycles")

        handleMissingCycles(f"{f}.csv")

        df = pd.read_csv(filepath, sep="\t", header=0)
        # os.remove(f"{f}.csv")
        print(f"INFO: removing - {f}.csv")
        return df.melt(
            id_vars=df.columns[:7],
            value_vars=df.columns[7:],
            var_name="Cycle Number",
            value_name="dRn"
        ).rename(columns=
            {"Well":"Well Position",
            "Dye": "Reporter"}
        )
    

        # print(f"removing: {f}.csv")

@st.cache_data
def read_df1(path):
    return pd.read_excel(
        path, skiprows=23, sheet_name="Amplification Data", engine="openpyxl"
    )

@st.cache_data
def read_df_results(path):
    return pd.read_excel(path, skiprows=23, sheet_name="Results", engine="openpyxl")

@st.cache_data
def read_df2(path):
    return pd.read_excel(
        path,
        sheet_name="Amplification Data",
        nrows=22,
        header=None,
        engine="openpyxl",
        names=["names", "values"],
    )

dfs = []
tab1, tab2 = st.tabs(["QuantStudio", "Name Generator"])
with tab1:
    st.info("Supported files: .rdlm from CFX or .eds file from Quantstudio platform")
   ## f"#### From Design Analysis software use Default export setting and tick 'Combine to one excel file' option"
    file_saved = st.file_uploader(
        "Upload file :sleeping: :", accept_multiple_files=False
    )

    if file_saved:
        if file_saved.name.endswith(".rdml"):
            run.load_any_zip(filename=file_saved)
            RDLM=True
            files = []
            for exp in run.experiments():
                for r in exp.runs():
                    # f"{r.tojson()}"
                    if r.tojson()['id'].startswith("Amp"):
                        data = r.export_table("amp")
                        files.append(r.tojson()['id'])
                        with open(f"{r.tojson()['id']}.csv", "w") as f:
                            f.write(data)
            for f in files:
                dfs.append(read_rdml_file(filepath=f"{f}.csv"))                    
            df = read_rdml(dfs)
        elif file_saved.name.endswith(".eds"):
            analysis_result_json = read_json_from_zip(file_saved,'primary/analysis_result.json')
            plate_setup = read_json_from_zip(file_saved,'setup/plate_setup.json')
            target_reporter_dict = {k['name']: k['reporter'] for k in plate_setup['targets']}
            well_format = plate_setup["blockType"].split("_")[1]

            EDS = True
            RDLM = False
            df = transform_json_to_df(wellResult=analysis_result_json['wellResults'],
                                      target_reporter_dict=target_reporter_dict,
                                      well_format=well_format)
        elif file_saved.name.endswith(".xlsx"):
            RDLM = False
            EDS = False
            df = read_df1(file_saved)
            df2 = read_df2(file_saved)
        else:
            st.warning("Unsupported file type.")
        col1, col2 = st.columns(2)
        if not RDLM | EDS:
            with col1:
                f"### Imported data", df
            with col2:
                f"### File Info", df2
        well_names = df["Well Position"].unique()
        target_names = df["Target"].unique()
        df

        # f"## Dataframe - Guessing Group Data"
        df["TargetName"] = df.Sample.str.split("_", expand=True).get(0).map(positive_ntc_group)
        df["Concentration"] = df.Sample.str.split("_", expand=True).get(2)
        df["Conditions"] = df.Sample.str.split("_", expand=True).get(4)
        df["Isolates"] = df.Sample.str.split("_", expand=True).get(1)
        df["Groups"] = df.TargetName.str.cat(df.Concentration, na_rep="", sep=" ")
        df["GroupsCondition"] = df.TargetName.str.cat([df.Concentration,df.Conditions], na_rep="", sep=" ")
        df["GroupsConditionIsolates"] = df.TargetName.str.cat([df.Concentration,df.Conditions, df.Isolates], na_rep="", sep=" ")
        
        if not RDLM | EDS:
            ret = read_df_results(file_saved)
            new = pd.merge(df, ret, on=["Target", "Well", "Well Position", "Sample"])
        else:
            new = df

        target_reporter = (
            new.groupby("Target")["Reporter"].unique().apply(list).to_dict()
        )

        target_color_mappings = {
            k: color_map.get(v[0]) for k, v in target_reporter.items()
        }
        if not RDLM | EDS:
            f"## Figures based on Target & Well position"
            well_selector = st.multiselect("Wells", well_names)
            target_selected = st.multiselect("Channel/Target", target_names)
            
            st.info(
                "If you want to display all filter data for given well. Only select from wells menu"
            )

            if well_selector and not target_selected:
                first_df = df[df["Well Position"].isin(well_selector)]
                fig1 = plot_figure(first_df,target_color_mappings)
                st.plotly_chart(fig1, theme=None, use_container_width=False)

            if not well_selector:
                st.info("please select a well!")
            # print(target_selected)
            if target_selected and well_selector:
                second_selection_df = df[
                    (df["Target"].isin(target_selected))
                    & (df["Well Position"].isin(well_selector))
                ]
                fig2 = plot_figure(second_selection_df,target_color_mappings)
                st.plotly_chart(fig2, theme=None, use_container_width=False)
        
        f"## Figures based on Target"
        basedOnTarget = st.multiselect("Targets", target_names, key="basedOnTargets")
        if basedOnTarget:
            # f"{basedOnTarget}"
            df_basedOnTarget = new[new['Target'].isin(basedOnTarget)]
            figs = plot_figure3(df_basedOnTarget, target_color_mappings,title_list=basedOnTarget)
            st.plotly_chart(figs,use_container_width=False)



        f"## Figures based on Concentration"
        secondtargets = st.multiselect(f"## Targets",df.Target.unique(), key="second")

        if secondtargets:
            for idx, grp in enumerate(new.Groups.unique(),1):
                grps = new[new["Groups"].isin([grp]) & (new["Target"].isin(secondtargets))]
                if grps.size >0:
                    config = dict(
                    displaylogo=False,
                    toImageButtonOptions={
                        "format": "png",
                        "scale": 10,
                        "filename": " ".join(([grp]+secondtargets)),
                    },
                    modeBarButtonsToRemove=[
                        "select2d",
                        "lasso2d",
                    ],
                )
                    figs = plot_figure2(grps, target_color_mappings,group_title="Groups")
                    st.plotly_chart(figs,use_container_width=False,config=config)
        f"## Figures based on Concentration & Condition"
        conentrationAndCondition = st.multiselect(f"## Targets",df.Target.unique(), key="third")
        
        # sub_fig = make_subplots(rows= 5, cols=1,shared_xaxes=False, shared_yaxes=False)
        # for idx, grp in enumerate(new.Groups.unique(),1):
        #     grps = new[new["Groups"].isin([grp])]
        #     figs = plot_figure2(grps, target_color_mappings,title=True)
        #     for fig in figs.data:
        #         sub_fig.add_trace(fig, row=idx, col=1)
        # new
        if conentrationAndCondition:
            for idx, grp in enumerate(new.GroupsCondition.unique(),1):
                print(grp)
                grps = new[new["GroupsCondition"].isin([grp]) & (new["Target"].isin(conentrationAndCondition))]
                if grps.size >0:
                    config = dict(
                    displaylogo=False,
                    toImageButtonOptions={
                        "format": "png",
                        "scale": 10,
                        "filename": " ".join(([grp]+conentrationAndCondition)),
                    },
                    modeBarButtonsToRemove=[
                        "select2d",
                        "lasso2d",
                    ],
                )
                    figs = plot_figure2(grps, target_color_mappings, group_title="GroupsCondition")
                    st.plotly_chart(figs,use_container_width=False,config=config)
            
        f"## Figures based on Concentration, Condition & Isolates"
        conentrationAndConditionAndIsolates = st.multiselect(f"## Targets",df.Target.unique(), key="fourth")
        
        # sub_fig = make_subplots(rows= 5, cols=1,shared_xaxes=False, shared_yaxes=False)
        # for idx, grp in enumerate(new.Groups.unique(),1):
        #     grps = new[new["Groups"].isin([grp])]
        #     figs = plot_figure2(grps, target_color_mappings,title=True)
        #     for fig in figs.data:
        #         sub_fig.add_trace(fig, row=idx, col=1)
        if conentrationAndConditionAndIsolates:
            for idx, grp in enumerate(new.GroupsConditionIsolates.unique(),1):
                grps = new[new["GroupsConditionIsolates"].isin([grp]) & (new["Target"].isin(conentrationAndConditionAndIsolates))]
                if grps.size >0:
                    config = dict(
                    displaylogo=False,
                    toImageButtonOptions={
                        "format": "png",
                        "scale": 10,
                        "filename": " ".join(([grp]+conentrationAndConditionAndIsolates)),
                    },
                    modeBarButtonsToRemove=[
                        "select2d",
                        "lasso2d",
                    ],
                )
                    figs = plot_figure2(grps, target_color_mappings,group_title="GroupsConditionIsolates")
                    st.plotly_chart(figs,use_container_width=False,config=config)        
            
    else:
        st.info("Awaiting run file")
with tab2:
    ret = st.text_area(
        "Enter your table here. Must be Tab sperated. First line must be the headers"
    )
    tbl_dict = {}
    if ret:
        header_ = ret.strip().splitlines()[0].split("\t")
        header_list = list(ret.strip().splitlines()[0].split("\t"))
        data_ = ret.rstrip().splitlines()[1:]
        for col in header_:
            if col in tbl_dict:
                st.warning(f"Following column name is duplicated, please rename: {col}")
                st.stop()
            tbl_dict[col] = []

        for k in data_:
            for key, val in zip(header_list, k.split("\t")):
                tbl_dict[key].append(val)
        df = pd.DataFrame(tbl_dict)
        "## Data Entered"

        st.write(df)
        # for more effienct see: https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-pandas-dataframe
        # i don't care about performance as the max rows will be <100. hence futile here.
        llll = []
        try:
            for rows in df.iterrows():
                for k in range(1, int(rows[1].Replicates) + 1):
                    llll.append(
                        f"{rows[1]['Sample Name']} {rows[1].Concentration} {rows[1].Unit} rep {k}"
                    )

            s = pd.Series(llll, name="Output Sequences")

            "## Output"
            st.write(s)
        except AttributeError:
            st.warning(
                "One or more column name missing, following column should be present: 'Sample Name', 'Concentration', 'Unit', 'Replicates' See Example table"
            )

    "## Example Data Table"
    example = pd.DataFrame(
        {
            "Sample Name": ["Bacteria 1", "Bacteria 2", "Bacteria 3"],
            "Concentration": [100, 200, 150],
            "Unit": ["org/mL", "org/mL", "org/mL"],
            "Replicates": [5, 3, 5],
        }
    )
    st.write(example)

    "### Example Output:"
    ex_out = []
    for rows in example.iterrows():
        for k in range(1, int(rows[1].Replicates) + 1):
            ex_out.append(
                f"{rows[1]['Sample Name']} {rows[1].Concentration} {rows[1].Unit} rep {k}"
            )
    st.write(pd.Series(ex_out, name="Output Sequences"))