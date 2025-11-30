import requests
from bs4 import BeautifulSoup

def check_wiki_columns():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        
        # Check header
        headers = [th.text.strip() for th in table.findAll('tr')[0].findAll('th')]
        print(f"Headers: {headers}")
        
        # Check first row
        first_row = table.findAll('tr')[1].findAll('td')
        row_data = [td.text.strip() for td in first_row]
        print(f"First Row: {row_data}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_wiki_columns()
