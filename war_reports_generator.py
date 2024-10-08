import sys
import time
import requests
import json
from datetime import datetime

"""----------------------MAIN-----------------------------------------"""
member_names = []
member_ids = []
war_Respect = []
war_hits = []
chain_bonus_hits_number_list = [25,50,100,250,500,1000,2500,5000,10000,25000,50000,100000]


def main(faction_id,war_id,leader_api_key,report_filename,progress_callback=None, stage_callback=None):

    # Fetching war attacks, war score, member names , member ids and war start and end time from the API
    def fetch_war_data(faction_id,war_id):
        global war_start_timestamp
        global war_end_timestamp
        war_report_url = f"https://api.torn.com/torn/{str(war_id)}?selections=rankedwarreport&key={leader_api_key}"
        war_data_api_reponse_json = requests.get(war_report_url).json()
        war_start_timestamp = str(war_data_api_reponse_json["rankedwarreport"]["war"]["start"])
        war_end_timestamp = str(war_data_api_reponse_json["rankedwarreport"]["war"]["end"] + 1)
        members_war_data = war_data_api_reponse_json["rankedwarreport"]["factions"][str(faction_id)]["members"]

        global member_names
        global member_ids
        global war_Respect
        global war_hits

        member_ids = [int(member_ids_war_data) for member_ids_war_data in members_war_data]
        member_names = [members_war_data[member_ids_war_data]["name"] for member_ids_war_data in members_war_data]
        war_hits = [int(members_war_data[member_ids_war_data]["attacks"]) for member_ids_war_data in members_war_data]
        war_Respect = [members_war_data[member_ids_war_data]["score"] for member_ids_war_data in members_war_data]
        
        with open(f"{report_filename}.warData.txt","w") as war_data_txt_file:
            war_data_txt_file.write(f"{war_start_timestamp}\n")
            war_data_txt_file.write(f"{war_end_timestamp}\n")
            for loop_variable in range(len(member_ids)):
                war_data_txt_file.write(f"{member_names[loop_variable]}\t\t\t{str(member_ids[loop_variable])}\t\t\t{str(war_hits[loop_variable])}\t\t\t{str(war_Respect[loop_variable])}")
                war_data_txt_file.write("\n")
        war_data_txt_file.close()
        if progress_callback:
            progress_callback(0, 100)

        if stage_callback:
            stage_callback("war data noted")
        print(member_names)
        print("war data noted")


    """-----------------------------------FUNCTIONSSS-----------------------------"""
    def assists(player_to_check):
        f =0
        with open(f"{report_filename}.attacks.txt",'r') as attacks_txt_file: 
            read = attacks_txt_file.read()
        attacks_txt_file.close()
        data  = json.loads(read)
        for key in data:
            attacker_id = data[key]["attacker_id"]
            if attacker_id == player_to_check:
                result = data[key]["result"]
                if str(result) == "Assist":
                    f+=1
        return f

    def fetch_attacks(start,end):
        stage_callback("Fetching attacks....")
        print("Fetching attacks....")
        current_end_timestamp = start
        attack_timestamp_steps = []
        with open(f"{report_filename}.attacks.txt", 'a') as a:
            while int(end) > int(current_end_timestamp):
                try:
                    url = f"https://api.torn.com/faction/?selections=attacks&from={str(current_end_timestamp)}&to={end}&key={leader_api_key}"
                    print(url)
                    data = requests.get(url).json()
                    if len(data["attacks"]) != 0: #checks if the response is empty
                        for key in data["attacks"]:
                            current_end_timestamp = data["attacks"][key]["timestamp_started"] +1
                        progress_callback(int(current_end_timestamp) - int(start), int(end) - int(start))
                        stage_callback(f"curently fetched till: {current_end_timestamp} ending at {end}")
                        print(f"curently fetched till: {current_end_timestamp} ending at {end}")
                        if current_end_timestamp not in attack_timestamp_steps: # chceks if a single attacks is fetched repeatedly
                            first_key = list(data["attacks"].keys())[0]
                            data = {key: value for key, value in data["attacks"].items() if key != first_key}
                            data = json.dumps(data, ensure_ascii=False)
                            a.write(str(data))
                            time.sleep(3)
                            attack_timestamp_steps.append(current_end_timestamp)
                        else:
                            break
                    else:
                        break
                except Exception as e:
                    print(e)
                    stage_callback(f"Error: {e}\n Please check and run again!")
                    print("An API exception occured, please delete the attacks.txt file, and run this command again!")
                    print("exiting the program")
                    exit()
        print("attacks noted")

    def numpy_sorted_array(unsorted_array):
        import numpy as np
        return np.argsort(-np.array(unsorted_array))


    def overall_respect_earned(player_to_check):
        hit_respect= respect_earned = 0
        with open(f"{report_filename}.attacks.txt",'r') as r:
            read = r.read()
        data  = json.loads(read)
        for key in data:
            attacker_id = data[key]["attacker_id"]
            if attacker_id == player_to_check:
                hit_respect = data[key]["respect"]
                respect_earned += hit_respect
        return respect_earned


    def overall_hit_count(player_to_check):
        hit_count= 0
        with open(f"{report_filename}.attacks.txt",'r') as r:
            read = r.read()
        data  = json.loads(read)
        for key in data:
            attacker_id = data[key]["attacker_id"]
            if attacker_id == player_to_check:
                if data[key]["result"] != "Lost" and data[key]["result"] != "Timeout":
                    hit_count += 1
        return hit_count


    def place_data_in_excel():
        from openpyxl import Workbook, load_workbook
        wbk = Workbook()
        main_sheet = wbk.active
        x = y =0
        corrected_index = numpy_sorted_array(war_hits)
        main_sheet["A1"] = "Names"
        main_sheet["b1"] = "War Hits"
        main_sheet["c1"] = "War Score"
        main_sheet["d1"] = "Overall Respect Earned"
        main_sheet["e1"] = "Bonuses"
        main_sheet["f1"] = "Respect lost"
        main_sheet["g1"] = "Assists"
        main_sheet["h1"] = "Overall hit count"
        for x in corrected_index:
            main_sheet[f"A{y+2}"] = member_names[x] +" [" + str(member_ids[x]) +"]"
            main_sheet[f"B{y+2}"] = war_hits[x]
            main_sheet[f"C{y+2}"] = war_Respect[x]
            main_sheet[f"D{y+2}"] = overall_respect_list[x]
            main_sheet[f"E{y+2}"] = bonus_hits_list[x]
            main_sheet[f"F{y+2}"] = respect_lost_list[x]
            main_sheet[f"g{y+2}"] = assist_hits_list[x]
            main_sheet[f"H{y+2}"] = hit_count_list[x]
            y +=1
        wbk.save(report_filename + ".xlsx")
        print("excel saved successfully")

    def positive_bonus_hits(player_to_check):
        respect_gain=0
        with open(f"{report_filename}.attacks.txt",'r') as r: 
            read = r.read()
        data  = json.loads(read)
        for key in data:
            attacker_id = data[key]["attacker_id"]
            if attacker_id == player_to_check:
                chain_bonus = data[key]["chain"]
                if chain_bonus in chain_bonus_hits_number_list:
                    respect_gain += data[key]["respect"]
        return respect_gain


    def respect_loss(player_to_check):
        total_respect_lost = hit_respect = 0
        with open(f"{report_filename}.attacks.txt",'r') as r:
            read = r.read()
        data  = json.loads(read)
        for key in data:
            defender_id = data[key]["defender_id"]
            if defender_id == player_to_check:
                war_check = data[key]["modifiers"]["war"]
                if war_check == 2:
                    hit_respect = data[key]["respect"]
                    total_respect_lost += hit_respect
        return total_respect_lost


    def replace_characters_in_file():
        with open(f"{report_filename}.attacks.txt",'r') as r:
            read = r.read()
        
        replaced_content = read.replace('}{', ", ")
        
        with open(f"{report_filename}.attacks.txt", 'w') as file:
            file.write(replaced_content)
        print("File contents changed to fit the script successfully")


    """------------------------- featching war data ----------------------------"""
    try:
        fetch_war_data(faction_id, war_id)
        print(war_start_timestamp, war_end_timestamp)
        
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stage_callback(f"Exception message: {exc_value}\n member names failed {exc_type}")
        print("Exception message:", exc_value)
        print("member names failed", exc_type)
        print("exiting now")
        exit()


    """------------------------- featching attacks ----------------------------"""
    fetch_attacks(war_start_timestamp, war_end_timestamp)
    replace_characters_in_file()
    stage_callback("attacks noted")
    """----------------------------- Assists ----------------------------------"""
    assist_hits_list = [assists(member_ids[x]) for x in range(len(member_ids))]

    print(assist_hits_list)
    stage_callback("assists counted successfully")
    print("assists counted successfully")

    """----------------------------- Overall respect earned ----------------------------------"""

    overall_respect_list = [overall_respect_earned(member_ids[x]) for x in range(len(member_ids))]

    print(overall_respect_list)
    stage_callback("Overall respect earned counted successfully")
    print("Overall respect earned counted successfully")

    """----------------------------- Respect lost per member ----------------------------------"""

    respect_lost_list = [respect_loss(member_ids[x]) for x in range(len(member_ids))]

    print(respect_lost_list)
    stage_callback("Respect lost per member counted successfully")
    print("Respect lost per member counted successfully")
    """----------------------------- Bonus Hits respect ----------------------------------"""

    bonus_hits_list = [positive_bonus_hits(member_ids[x]) for x in range(len(member_ids))]

    print(bonus_hits_list)
    stage_callback("Bonus hits counted successfully")
    print("Bonus hits counted successfully")

    """-----------------------------Overall Hit count----------------------------------"""

    hit_count_list = [overall_hit_count(member_ids[x]) for x in range(len(member_ids))]

    print(hit_count_list)
    stage_callback("Overall hits counted successfully")
    print("Overall hits counted successfully")
    print("Data processing completed successfully")

    place_data_in_excel()
    stage_callback("Data processing completed successfully")