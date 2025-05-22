from flask import Flask, render_template, request, redirect, url_for
from fin.model import load_data_from_db, preprocess_data, get_top_10_best_value_tours
import joblib
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Загрузка модели при старте приложения
model = joblib.load('tour_purchase_model.pkl')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_tours', methods=['POST'])
def find_tours():
    # Получаем данные из формы
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    top_n = int(request.form['top_n'])
    
    # Преобразуем даты в месяцы
    start_month = datetime.strptime(start_date, '%Y-%m-%d').month
    end_month = datetime.strptime(end_date, '%Y-%m-%d').month
    
    # Загружаем и предобрабатываем данные
    df = load_data_from_db()
    df = preprocess_data(df)
    
    # Фильтруем туры по датам
    filtered_tours = df[
        (df['start_month'] >= start_month) & 
        (df['end_month'] <= end_month)
    ].copy()
    
    if len(filtered_tours) == 0:
        return render_template('results.html', 
                             message="Не найдено туров на указанные даты")
    
    # Добавляем предсказание оптимальности
    features = ['price', 'start_month', 'end_month', 'location', 
               'tour_type', 'rating', 'rating_count']
    filtered_tours['optimal_score'] = model.predict_proba(
        filtered_tours[features]
    )[:,1]
    
    
    # После фильтрации и сортировки
    best_tours = get_top_10_best_value_tours(filtered_tours, model, top_n)

    # Преобразуем в список словарей для шаблона
    tours_list = best_tours[[
        'name', 'price', 'dates', 'url', 'price_score'
    ]].to_dict('records')
    
    return render_template('results.html', 
                         tours=tours_list,
                         start_date=start_date,
                         end_date=end_date)

if __name__ == '__main__':
    app.run(debug=True)