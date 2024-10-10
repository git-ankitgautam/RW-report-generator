import streamlit as st
from war_reports_generator import main
import os

st.set_page_config(page_title="RW Report Generator")
def cleanup():
    try:
        os.remove(f"{filename}.xlsx")
        os.remove(f"{filename}.attacks.txt")
        os.remove(f"{filename}.warData.txt")
    except:
        pass

def update_progress(current_step, total_steps):
    progress = (current_step / total_steps)
    progress_bar.progress(progress)

def update_stage(stage_message):
    stage_text.text(stage_message)


st.title("RW Report Generator")
#make two columns to show the text boxes
column1, column2 = st.columns(2)

faction_id = column1.text_input("Faction ID:")
leader_api_key = column2.text_input("Leader/AA member API Key:")
war_id = column1.text_input("War ID:")
filename = column2.text_input("Filename:")


if st.button("Generate Report"):
    progress_bar = st.progress(0)
    stage_text = st.text("")
    #main(faction_id, war_id, str(leader_api_key),str(filename),progress_callback=update_progress, stage_callback=update_stage)
    with open(f"{filename}.xlsx", 'rb') as excel_file:
        pass
    st.download_button("Download report file",data=excel_file, file_name=filename + ".xlsx", on_click=cleanup())
    excel_file.close()