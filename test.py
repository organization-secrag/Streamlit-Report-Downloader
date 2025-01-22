import requests
import json

response = requests.get('https://www.sec.gov/files/company_tickers.json', headers={'User-Agent': 'paul.bezko@hotmail.com'})

# Check if the request was successful
if response.status_code == 200:
    data = response.json()  # This method is more convenient than json.loads(response.text)

    # Check if data is a dictionary
    if isinstance(data, dict):
        remade_data = {item['title']: item['cik_str'] for item in data.values()}

        remade_json = json.dumps(remade_data, indent=2)

        with open('titles_ciks.json', 'w') as f:
            f.write(remade_json)
    else:
        print("The response data is not a dictionary.")
else:
    print("Failed to retrieve data. Status code: ", response.status_code)