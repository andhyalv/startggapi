import requests
import json
import pandas as pd

pd.set_option('display.max_colwidth',None)
API_TOKEN = "70f0dd699921dba321fe3f10cbe0d112"
url = "https://api.start.gg/gql/alpha"
body = """
query attendees($tourneySlug : String!, $page: Int!, $perPage: Int!){
  tournament(slug: $tourneySlug){
    numAttendees
    participants(query:{
      page: $page
      perPage: $perPage
    })
    {
      nodes{
        gamerTag
      }
    }
  }
},
"""
variables = {
  "tourneySlug" : "big-dapple-9",
  "page" : 1,
  "perPage" : 500,
  "SplatoonID" : 36202,
  "limit" : 10
}

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

df = pd.json_normalize(data['data']['tournament']['participants']['nodes'])
print(df)

