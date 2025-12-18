import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Загружаем данные
@st.cache_data
def load_hist_data():
    url = 'https://raw.githubusercontent.com/smorchkova001-git/weather-analysis-dashboard/refs/heads/main/historical_data.csv'
    return pd.read_csv(url)

hist_data = load_hist_data()

# Реализовываем KMeans
def KMeans_city(df):
    lst = []
    for city in df['city'].unique():
        city_data = df[df['city'] == city]
        lst.append({
            'city': city,
            'mean': city_data['temperature'].mean(),
            'amp': city_data['temperature'].max() - city_data['temperature'].min(),
            'winter': city_data[city_data['season'] == 'winter']['temperature'].mean(),
            'summer': city_data[city_data['season'] == 'summer']['temperature'].mean()
        })
    
    data = pd.DataFrame(lst)
    
    # Кластеризация
    X = data[['mean', 'amp', 'winter', 'summer']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Для 15 городов достаточно кластеризации на 4 кластера
    kmeans = KMeans(n_clusters=4, random_state=42)
    data['cluster'] = kmeans.fit_predict(X_scaled)
    
    fig = px.scatter(
        data, 
        x='mean', 
        y='amp', 
        color='cluster',
        text='city',
        labels={'mean': 'Средняя температура (°C)', 'amp': 'Размах (°C)'}
    )
    
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig)
    
    return data

st.title('Кластеризация городов по температуре')
results = KMeans_city(hist_data)

st.write('Результаты кластеризации:')
st.dataframe(results.sort_values('cluster').reset_index(drop=True))

# Ссылка на GitHub
with st.sidebar:
    st.markdown("---")
    st.markdown("**👩‍💻 Автор:** Сморчкова Юлиана")
    st.markdown("**🔗 Подробнее на** [GitHub](https://github.com/smorchkova001-git/weather-analysis-dashboard)")
    st.markdown("---")