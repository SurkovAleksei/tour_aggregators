from parser import parse_site
from database import create_table
import time

def main():
    START_PAGE = 1
    END_PAGE = 3
    DELAY = 2
    
    print("Начало парсинга...")
    start_time = time.time()
    tours = parse_site(start_page=START_PAGE, end_page=END_PAGE, delay=DELAY)

if __name__ == "__main__":
    main()