import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Загрузка данных из БД 
def load_data_from_db(db_path='tours.db'):
    try:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM tours"
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        print(f"Ошибка при работе с SQLite: {e}")
        return pd.DataFrame() 
    finally:
        if 'conn' in locals():
            conn.close()

# Предобработка данных
def preprocess_data(df):
    # Исправленная функция очистки цены
    def clean_price(price_str):
        if pd.isna(price_str):
            return np.nan
        cleaned = str(price_str).strip()
        cleaned = cleaned.replace('RUB', '').replace('€', '1').replace(' ', '').replace(',', '')
        try:
            return float(cleaned)
        except ValueError:
            return np.nan
    
    df['price'] = df['price'].apply(clean_price)
    
    # Исправленная обработка даты
    def process_dates(date_str):
        if pd.isna(date_str):
            return np.nan, np.nan
        parts = date_str.split('—')
        start_month = extract_month(parts[0].strip())
        end_month = extract_month(parts[1].strip()) if len(parts) > 1 else np.nan
        return start_month, end_month
    
    # Применяем функцию к dates и создаем колонки
    df[['start_month', 'end_month']] = df['dates'].apply(
        lambda x: pd.Series(process_dates(x))
    )
    
    # Кодирование категориальных переменных
    cat_cols = ['location', 'tour_type']
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].fillna('Unknown'))
    
    # Заполнение пропусков
    df.fillna({
        'rating': 0,
        'rating_count': 0,
        'start_month': df['start_month'].mode()[0],
        'end_month': df['end_month'].mode()[0],
        'price': df['price'].median()
    }, inplace=True)
    
    return df

def extract_month(date_str):
    month_map = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    for month_name, month_num in month_map.items():
        if month_name in date_str:
            return month_num
    return np.nan

def define_target(df):
    df['optimal_purchase_month'] = df['start_month']
    df['optimal_purchase_month'] = df['optimal_purchase_month'].apply(lambda x: x + 12 if x < 1 else x)
    return df

def train_model(df):
    features = ['price', 'start_month', 'end_month', 'location', 'tour_type', 'rating', 'rating_count']
    target = 'optimal_purchase_month'
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print("Отчет о классификации:")
    print(classification_report(y_test, model.predict(X_test)))
    
    return model

def get_top_10_best_value_tours(df, model, dt=10):
    df = predict_for_all_tours(df, model)
    df['price_score'] = df.apply(calculate_price_score, axis=1)
    top_tours = df.sort_values('price_score', ascending=False).head(dt)
    result = top_tours[[
        'name', 
        'price', 
        'dates',
        'rating',
        'rating_count',
        'optimal_purchase_month',
        'price_score',
        'url'
    ]]
    
    return result.reset_index(drop=True)
def predict_for_all_tours(df, model):
    #модель предсказания оптимальных туров для покупки
    df_processed = preprocess_data(df.copy())
    features = ['price', 'start_month', 'end_month', 'location', 'tour_type', 'rating', 'rating_count']
    X = df_processed[features]
    df['optimal_purchase_month'] = model.predict(X)
    return df


    
def calculate_price_score(row):
    #расчет оптимальности цены по цене и рейтингу и кол-ву отзывов
    rating_score = float(row['rating']) / 5
    cout_rat = float(row['rating_count']) / 100
    price_score = 1 / (row['price'] + 1)
    return 0.9 * rating_score + 0.3 * price_score + 0.001 * cout_rat

# Основной процесс
df = load_data_from_db()
print(f"Загружено {len(df)} туров")

df = preprocess_data(df)
print("\nПосле предобработки:")
print(df[['name', 'price', 'start_month', 'end_month']].head())

df = define_target(df)
model = train_model(df)

if not df.empty:
    df_with_predictions = predict_for_all_tours(df, model)
    #print(df_with_predictions[['name', 'dates', 'optimal_purchase_month']])
    
# Сохранение модели
joblib.dump(model, 'tour_purchase_model.pkl')
print("\nМодель сохранена в tour_purchase_model.pkl")

# Проверка на нескольких примерах
sample = df.sample(3)
features = ['price', 'start_month', 'end_month', 'location', 'tour_type', 'rating', 'rating_count']
print("\nПримеры предсказаний:")
for _, row in sample.iterrows():
    prediction = model.predict([row[features]])[0]
    print(f"\nТур: {row['name']}")
    print(f"Даты: {row['dates']}")
    print(f"Предсказанный оптимальный месяц покупки: {prediction}")