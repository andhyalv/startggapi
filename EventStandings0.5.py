import requests
import json
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

#dataframe creation options
pd.options.mode.copy_on_write = True
pd.set_option('display.max_colwidth',None)

#API info, google drive json files, sheets setup.
API_TOKEN = "70f0dd699921dba321fe3f10cbe0d112"
url = "https://api.start.gg/gql/alpha"
credentials = 'C:/Users/andhy/Desktop/code/scripts/StartGG/credentials-sheets.json'
authorized_user = 'C:/Users/andhy/Desktop/code/scripts/StartGG/authorized_user.json'
gc = gspread.oauth()
SheetsID = "1KMcrNygaSwDygcz8pCLL0VeqDECsHxVXgGhaoF0E7gM"
sh = gc.open_by_key(SheetsID)
worksheet_name = 'PlacementImport'
worksheet = sh.worksheet(worksheet_name)
dfSheets = get_as_dataframe(worksheet)

#Query made to the StartGG API.
body = """
query EventStandings($tourneySlug: String!, $page: Int!, $perPage: Int!) {
  event(slug: $tourneySlug) {
    standings(query: { page: $page, perPage: $perPage }) {
      nodes {
        placement
        entrant {
          name 
          participants {
            gamerTag
            user {
              discriminator
            }
          }
        }
      }
    }
  }
},
"""
#Variables header to be passed to the query.
variables = {
  "tourneySlug" : input("Enter Tournament Slug"),
  "page" : 1,
  "perPage" : 500,
}

#Headers passed to the query, along with the query and variables itself.
payload = {"query": body,
            "variables": variables}
headers = {"Authorization": "Bearer 70f0dd699921dba321fe3f10cbe0d112",
"Content-Type": "application/json"}

# Send the POST request
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)    

df = pd.json_normalize(data['data']['event']['standings']['nodes'])

#Creating a cleaned dataframe from the previous one.
column_names = ["gamerTag", "user.discriminator", "teamname", "placement"]
rows = []

for x in range(len(df)):
    participants = df.loc[x, "entrant.participants"]

    for p in participants:
        user = p.get("user")
        if not user or "discriminator" not in user:
            continue

        rows.append([
            p.get("gamerTag"),
            user.get("discriminator"),
            df.loc[x, "entrant.name"],
            df.loc[x, "placement"]
        ])

df1 = pd.DataFrame(rows, columns=column_names)


# Create an event ID via user input for the new Dataframe.
new_col_values = input("Enter the Event ID: ")
df1.insert(loc=0, column='EventID', value=(new_col_values))


#Apppend Queried Dataframe into Google Sheets Dataframe via Concat function.
df_list = df1.values.tolist()
#Upload new merged Dataframe to Google Sheets.
row = 1
col = 1
worksheet.append_rows(df_list)
