# Sleeper_Fantasy_Football_Scripts
Some scripts I wrote for my yearly FTA league


Assumes the existence of a "Main" account that exists (as a team owner, administrator, etc) in multiple leagues. These are the leagues the data will be pulled from. 


**ADP Comparison Script**
Pulls data from the "master" account's leagues from the provided league that use the provided team size and roster size. 
Pulls the draft data from the provided comparison draft ID (must be a part of the  "master" account's leagues <- TODO)

Creates an excel sheet of the draft data for every player picked in the leagues, exclusive of the comparison draft.
Creates an excel sheet of the comparison draft, adding where the player was picked in relationship to their ADP across the other leagues. (a negative number means a player was picked too early compared to ADP, a positive number means the pick was a "steal").

Automatically formats the comparison draft data in snake format so each team is a singular column.
