import requests
from bs4 import BeautifulSoup

# Function to check ticket availability
def check_tickets():
    url = 'https://tixel.com/au/music-tickets/2024/04/12/sonny-fodera-170-russell-melbour'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for the specific div element indicating tickets are available
    ticket_available = soup.find_all('div', class_='space-y-3 text-left')
    if ticket_available:
        print("Tickets are available!")
    else:
        print("No tickets available.")

# Main logic
if __name__ == '__main__':
    check_tickets()
