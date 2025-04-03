import requests
from bs4 import BeautifulSoup
import time

"""Вызов функции parse_site(start_page=1, end_page=3, delay=2)
start_page - начальная страница
end_page - конечная страница
delay - задержка между запросами """
def parse_site(start_page=1, end_page=1, delay=1):
    for page in range(start_page, end_page + 1):
        # Запрос к сайту
        url = f"https://bolshayastrana.com/tury?plainSearch=1&page={page}"
        print(f"Парсинг страницы {page}")
        
        # Запрос к сайту get запросом
        response = requests.get(url)
        
        # Проверка
        if response.status_code == 200:
            # Объект HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Данные из tour-preview__title
            titles = soup.find_all('tour-preview__title')
            for title in titles:
                print(title.text)
            
            # Находим все элементы с турами
            tours = soup.find_all('div', class_='tour-preview')
            
            for tour in tours:
                try:
                    # Название тура
                    name = tour.find('div', itemprop='name').get_text(strip=True)
                    
                    # URL тура 
                    url = tour.find('meta', itemprop='url')['content']
                    full_url = f"https://bolshayastrana.com{url}" 
                    
                    # Цена 
                    price = tour.find('span', itemprop='price').get_text(strip=True)
                    
                    # Дата
                    dates = tour.find('span', class_='tour-preview__details-caption').get_text(strip=True)
                    
                    # Описание
                    description = tour.find('div', itemprop='description').get_text(strip=True)
                    
                    # Местоположение
                    location = tour.find('div', class_='tour-preview__location').get_text(strip=True)
                    
                    # Тип тура
                    tour_type = tour.find('a', class_='as-tag is-small').get_text(strip=True)
                    
                    # Рейтинг
                    rating = tour.find('meta', itemprop='ratingValue')['content']
                    rating_count = tour.find('meta', itemprop='ratingCount')['content']
                    
                    # Изображение
                    image = tour.find('meta', itemprop='image')['content']
                    
                    # Все данные 
                    print(f"Название: {name}")
                    print(f"URL: {full_url}")
                    print(f"Цена: {price}")
                    print(f"Даты: {dates}")
                    print(f"Местоположение: {location}")
                    print(f"Тип тура: {tour_type}")
                    print(f"Рейтинг: {rating} (оценок: {rating_count})")
                    print(f"Изображение: {image}")
                    print(f"Описание: {description[:100]}...") 
                    print("="*50)
                
                except Exception as e:
                    print(f"Ошибка при парсинге тура: {e}")
                    continue
            
            # Задержка м.д. запросами
            if page < end_page:
                time.sleep(delay)
        else:
            print(f"Ошибка {response.status_code} на странице {page}")
            break