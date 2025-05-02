from parser import parse_site
from database import create_connection, create_table, insert_tour, get_tours
import time

def main():
    # Настройки парсинга
    START_PAGE = 1
    END_PAGE = 100
    DELAY = 2
    
    # Парсингсайта
    print("Начало парсинга...")
    start_time = time.time()
    tours = parse_site(start_page=START_PAGE, end_page=END_PAGE, delay=DELAY)
    print(f"Получено {len(tours)} туров за {time.time() - start_time:.2f} секунд")
    
    #Сохранение данных в БД
    conn = create_connection()
    if conn:
        create_table(conn)
        
        inserted_count = 0
        for tour in tours:
            if insert_tour(conn, tour):
                inserted_count += 1
        
        print(f"Добавлено {inserted_count} новых туров в базу данных")
        
        #Просмотр результатов
        print("\nПоследние добавленные туры:")
        for tour in get_tours(conn, 5):
            print(f"\nID: {tour[0]}")
            print(f"Название: {tour[1]}")
            print(f"Цена: {tour[2]}")
            print(f"Даты: {tour[3]}")
            print(f"URL: {tour[4]}")
            print("-" * 50)
        
        conn.close()
    else:
        print("Не удалось подключиться к базе данных")

if __name__ == "__main__":
    main()