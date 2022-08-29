import numpy as np
import pandas as pd
from sleeper_wrapper import User, Drafts, Players
#from collections import defaultdict


#Master User
DATA_USER = User("FTAFFL")
#DATA_USER = User("RUFFLMOD")
#Year 
YEAR = 2022
#Size of the starting roster
LEAGUE_SIZE = 14
#Roster positions
ROSTER = ['QB', 'RB', 'RB', 'WR', 'WR', 'WR', 'TE', 'FLEX', 'K', 'DEF', 'BN', 'BN', 'BN', 'BN', 'BN', 'BN']
#ID of the draft to compare
DRAFT_ID = "851201595885621248"
#DRAFT_ID = "856680945577754624"
#Whether or not it's a snake draft
SNAKE = True


#Returns the pick data (player ID and pick #) from each relevant draft
def get_data():
    league_df = pd.DataFrame()
    comparison_df = pd.DataFrame()
    #Iterates through each league the master account is in
    for league in DATA_USER.get_all_leagues("nfl", YEAR):
        #Only grabs leagues that match the LEAGUE_SIZE and ROSTER, and have already started or finished drafting. 
        if league["total_rosters"] == LEAGUE_SIZE and (league["status"] == "drafting" or league["status"] == "in_season"):
            draft_id = league["draft_id"]
            #Gets the pick data from the draft
            temp_df = create_pick_df(draft_id)
            if draft_id == DRAFT_ID:
                league_df = temp_df
            else:
                if comparison_df.empty:
                    comparison_df = temp_df
                else:
                    #Two different ways of combining the dataframes, time difference appears to be negligible
                    #comparisonDF = pd.merge(comparisonDF, tempDF, on = "player_id", how = "outer")
                    comparison_df = pd.concat([comparison_df, temp_df], axis = 1)
    #Gets the comparison data if the league to be compared isn't under the master account's umbrella
    if league_df.empty:
        league_df = create_pick_df(DRAFT_ID)
    return comparison_df, league_df


#Creates a dataframe of the picks in each league's draft. Only keeps the player_id and pick_no data
#Ran into an issue where the same player had a different name in different drafts, so the pick data wasn't properly coombined. 
#Instead players are stored by their ID and then mapped to their names later
def create_pick_df(draft_id):
    temp_df = pd.DataFrame()
    draft_results = Drafts(draft_id).get_all_picks()
    temp_df = pd.json_normalize(draft_results)
    temp_df = temp_df[["player_id", "pick_no"]].set_index("player_id")
    return temp_df


#Creates the Mininimum Pick, Maximum Pick, and ADP columns for comparison.
def get_adp(input_df):
    input_df["Min"], input_df["Max"], input_df["ADP"] = input_df.min(axis = 1), input_df.max(axis = 1), input_df.mean(axis = 1)
    input_df = input_df[["Min", "Max", "ADP"]]
    return input_df


#Gets a mapping of player_id to player name
def get_players_df():
    players = Players().get_all_players()
    temp_df = pd.DataFrame.from_dict(players).transpose()
    temp_df["Name"] = temp_df["first_name"] + " " + temp_df["last_name"]
    temp_df = temp_df["Name"]
    return temp_df


#Maps each player ID to the player's name
def assign_player_names(input_df, players_df):
    temp_df = input_df.join(players_df).set_index("Name")
    return temp_df


#Merges the league_df with the adp_df, then the players_df to replace player IDs with player names
#Adds the Min / Max tag to players
#Formats the picks in snake / non snake draft order
def create_final_df(adp_df, league_df, players_df):
    final_df = pd.merge(adp_df, league_df, on = "player_id", how = "outer")
    final_df["Diff"] = final_df["pick_no"] - final_df["ADP"] 
    final_df = assign_player_names(final_df, players_df)
    final_df = final_df[final_df["pick_no"].notna()].sort_values(by = ["pick_no"])
    #final_df = final_df.sort_values(by = ["pick_no"])

    #DataDict is used to store the draft data in snake order (Every other draft round is reversed)
    #dataDict = defaultdict(list)
    '''This appears to be just barely faster than defaultdict'''
    data_dict = {}
    for i in range(1, LEAGUE_SIZE + 1):
        data_dict[str(i)] = []
        data_dict[str(i) + " - Val"] = []
    for i, (index, row) in enumerate(final_df.iterrows()):
        if row["pick_no"] < row["Min"]:
            index = index + " MIN"
        elif row["pick_no"] > row["Max"]:
            index = index + " MAX"
        #Puts odd number draft rounds in normal order
        if int(i / LEAGUE_SIZE)%2 == 0:
            data_dict[str(i % LEAGUE_SIZE + 1)].append(index)
            data_dict[str(i % LEAGUE_SIZE + 1) + " - Val"].append(round(row["Diff"], 1))
        #Reverses even number draft rounds if SNAKE == True
        elif SNAKE:
            data_dict[str(LEAGUE_SIZE - i % LEAGUE_SIZE)].append(index)
            data_dict[str(LEAGUE_SIZE - i % LEAGUE_SIZE) + " - Val"].append(round(row["Diff"], 1)) 
        #If SNAKE == False then puts even number rounds in normal order as well
        else:
            data_dict[str(i % LEAGUE_SIZE + 1)].append(index)
            data_dict[str(i % LEAGUE_SIZE + 1) + " - Val"].append(round(row["Diff"], 1))
    #If a draft is unfinished, appends an empty line to the dictionary key so it can be made into a dataframe
    for key in data_dict:
        if len(data_dict[key]) < len(data_dict["1"]) or len(data_dict[key]) < len(data_dict[str(LEAGUE_SIZE)]):
            data_dict[key].append(np.nan)
    df = pd.DataFrame.from_dict(data_dict)
    return df


#Main
def main():
    #Gets the draft data from the master account's leagues and the specified comparison league
    comparison_df, league_df = get_data()
    #Gets the ADP, Min, and Max pick for each player in the master account's leagues' drafts
    adp_df = get_adp(comparison_df)
    #Gets a map of player_ids to player names
    players_df = get_players_df()
    #Creates the final draft display of picks and their ADP comparisons
    final_df = create_final_df(adp_df, league_df, players_df)
    #Maps the player names to the draft data from the master account's leagues
    comparison_df = assign_player_names(comparison_df, players_df)
    #Saves the individual draft data from the master account
    comparison_df.to_excel("FTAtotal_draft_stats.xlsx")
    #Saves the final draft display
    final_df.to_excel("FTAcomparison_draft_data.xlsx") 

if __name__ == "__main__":
    main()