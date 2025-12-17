import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Загружаем статистику
@st.cache_data
def load_stats():
    url = 'https://raw.githubusercontent.com/smorchkova001-git/weather-analysis-dashboard/refs/heads/main/city_season_stats.csv'
    return pd.read_csv(url)

stats = load_stats()
API_KEY = st.secrets['OPENWEATHER_API_KEY']

# Функция для получения погоды
def city_weather(CITY, API_KEY):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            'city': CITY,
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    elif response.status_code == 401:
        return {"error": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}
    else:
        return {"error": f'Unknown error: {response.status_code}'}

# Функция для проверки аномалии
def check_anomaly(city, current_temp, stats):
    month = datetime.now().month
    
    month_to_season = {12: "winter", 1: "winter", 2: "winter",
                   3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "summer",
                   9: "autumn", 10: "autumn", 11: "autumn"}
    current_season = month_to_season[month]
    city_stats = stats[(stats['city'] == city) & (stats['season'] == current_season)]
    
    mean_temp = city_stats['season_city_mean'].iloc[0]
    std_temp = city_stats['season_city_std'].iloc[0]
    
    # Находим пределы
    min_bound = mean_temp - 2 * std_temp
    max_bound = mean_temp + 2 * std_temp
    
    if current_temp > max_bound:
        result = f'Аномально высокая температура'
        anomaly_type = "high"
    elif current_temp < min_bound:
        result = f'Аномально низкая температура'
        anomaly_type = "low"
    else:
        result = f'Температура в пределах нормы'
        anomaly_type = "normal"
    
    return result, mean_temp, std_temp, anomaly_type


def main():
    st.title('Мониторинг текущих погодных условий')
    
    # Выбор города
    cities = list(stats['city'].unique())
    selected_city = st.selectbox('Выберите город', cities, index=cities.index('Moscow'))
    
    # словарь с переводом для самых частых типов описаний погоды
    translations = {
    "clear sky": "☀️ ясное небо",     
    "few clouds": "🌤️ небольшая облачность",
    "scattered clouds": "⛅ переменная облачность",       
    "broken clouds": "⛅ облачно с прояснениями", 
    "overcast clouds": "☁️ пасмурно", 

    "dust": "💨 пыль",                     
    "mist": "🌫️ туман",                         
    "smoke": "💨 смог",    
    "haze": "🌫️ дымка",

    "light rain": "🌦️ небольшой дождь",
    "moderate rain": "🌧️ умеренный дождь",
    "heavy intensity rain": "🌧️ сильный дождь",
    "very heavy rain": "⛈️ очень сильный дождь",
    "extreme rain": "⛈️ ливень",
    
    "snow": "❄️ снег",
    "heavy snow": "❄️ сильный снег"}

    
    # Кнопка для получения текущей температуры
    if st.button('Выполнить') and API_KEY:
        result = city_weather(selected_city, API_KEY)
            
        # Проверяем наличие ошибки
        if 'error' in result:
            if 'Invalid API key' in result['error']:
                st.error(result['error'])
            else:
                st.error(f"Ошибка: {result['error']}")
        else:
            # Отображаем данные о погоде
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Температура', f"{result['temperature']:.1f}C")
                st.metric('Ощущается как', f"{result['feels_like']:.1f}C")
            with col2:
                st.metric('Давление', f"{result['pressure']} hPa")
                st.metric('Влажность', f"{result['humidity']}%")
            with col3:
                st.metric('Скорость ветра', f"{result['wind_speed']} м/с")
                st.write("**Описание:**")
                desc = translations[result['description']] if result['description'] in translations else result['description']
                st.markdown(f'<p style="font-size:20px; ">{desc}</p>', unsafe_allow_html=True) 
                
                
            # Проверка аномалии
            anomaly_result, mean_temp, std_temp, anomaly_type = check_anomaly(selected_city, result['temperature'], stats)
            
            # Красиво оформляем результат проверки аномалии
            if anomaly_type:
                if anomaly_type == 'high':
                    st.error(anomaly_result)
                elif anomaly_type == 'low':
                    st.warning(anomaly_result)
                else:
                    st.success(anomaly_result)
                    
                # Показываем статистику
                st.info(f"**Средняя температура для текущего сезона:** {mean_temp:.1f}C\n\n"
                        f"**Стандартное отклонение:** {std_temp:.1f}C\n\n"
                        f"**Нормальный диапазон:** от {mean_temp - 2 * std_temp:.1f}C до {mean_temp + 2 * std_temp:.1f}°C")
            else:
                st.warning(anomaly_result)

            st.write(f"*Время запроса: {result['current_time']}*")

if __name__ == "__main__":
    main()

# Ссылка на GitHub
with st.sidebar:
    st.markdown("---")
    st.markdown("**👩‍💻 Автор:** Сморчкова Юлиана")
    st.markdown("**🔗 Подробнее на** [GitHub](https://github.com/smorchkova001-git/weather-analysis-dashboard)")
    st.markdown("---")