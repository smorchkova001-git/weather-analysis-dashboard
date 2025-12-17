import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
st.title('Анализ исторических данных')

# Загружаем данные
@st.cache_data
def load_hist_data():
    url = 'https://raw.githubusercontent.com/smorchkova001-git/weather-analysis-dashboard/refs/heads/main/historical_data.csv'
    return pd.read_csv(url)

@st.cache_data
def load_stats():
    url = 'https://raw.githubusercontent.com/smorchkova001-git/weather-analysis-dashboard/refs/heads/main/city_season_stats.csv'
    return pd.read_csv(url)

hist_data = load_hist_data()
stats = load_stats()

# Обработка данных
hist_data = hist_data.drop(['season_city_mean', 'season_city_std'], axis=1)

cities = list(stats['city'].unique())
city_selected = st.selectbox('Выберите город', options=cities, index=cities.index('Moscow'))
hist_city = hist_data[hist_data['city'] == city_selected].sort_values('timestamp').reset_index(drop=True)
hist_city['timestamp'] = pd.to_datetime(hist_city['timestamp'])

city_stats = stats[stats['city'] == city_selected].reset_index(drop=True)

#=====================ДАТАСЕТ=====================
st.subheader(f'Шаг 1: Датасет исторических данных температуры для города {city_selected}')
cols_selected = st.multiselect('Выберите колонки для отображения', options=hist_city.columns)
if cols_selected:
    st.dataframe(hist_city[cols_selected].drop_duplicates().reset_index(drop=True))
else:
    st.write(hist_city)

#=====================ОСНОВНЫЕ СТАТИСТИКИ=====================
st.subheader(f'Шаг 2: Основные статистики датасета с историческими данными температуры для города {city_selected}')
st.write(hist_city.describe())

#=====================ВИЗУАЛИЗАЦИЯ ТЕМПЕРАТУРЫ С АНОМАЛИЯМИ=====================
st.subheader(f'Шаг 3: График температуры для города {city_selected}')

# Очень много дат, поэтому нужно дать возможность выбрать период
min_date = hist_city['timestamp'].min().date()
max_date = hist_city['timestamp'].max().date()

st.write('Выберите период:')
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input('Начало', value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input('Окончание', value=max_date, min_value=min_date, max_value=max_date)

# Фильтруем данные
filtered_data = hist_city[(hist_city['timestamp'] >= pd.to_datetime(start_date)) & (hist_city['timestamp'] <= pd.to_datetime(end_date))]

fig = go.Figure()

# 1. Температура
fig.add_trace(go.Scatter(
    x=filtered_data['timestamp'],
    y=filtered_data['temperature'],
    mode='lines',
    name='Температура',
    line=dict(color='#4aab6b', width=1.5),
    opacity=0.8))

# 2. Скользящее среднее
fig.add_trace(go.Scatter(
    x=filtered_data['timestamp'],
    y=filtered_data['mov_av'],
    mode='lines',
    name='Скользящее среднее',
    line=dict(color='#ffad8f', width=2.5)))

# 3. Аномалии
anomalies = filtered_data[filtered_data['anomaly'] == 1]
if len(anomalies) > 0:
    fig.add_trace(go.Scatter(
        x=anomalies['timestamp'],
        y=anomalies['temperature'],
        mode='markers',
        name='Аномалии',
        marker=dict(color='#d62728', size=10, opacity=0.9)))


fig.update_layout(
    title=f'Температура в {city_selected} ({start_date} - {end_date})',
    xaxis_title='Дата',
    yaxis_title='Температура (C)',
    height=700,
    legend=dict(
        yanchor="top",
        xanchor="right"),
    xaxis=dict(
        tickangle=15,
        rangeslider=dict(visible=True)))

st.plotly_chart(fig)

#=====================ДАТАСЕТ СО СТАТИСТИКАМИ ПО ГОРОДАМ И СЕЗОНАМ=====================
st.subheader(f'Шаг 4: Датасет со статистикой по сезонам для города {city_selected}')
st.dataframe(city_stats)

#==============================================================
st.subheader(f'Шаг 5: Сезонные профили температуры для города {city_selected}')

seasons = ['winter', 'spring', 'summer', 'autumn']
city_stats['season'] = pd.Categorical(city_stats['season'], categories=seasons, ordered=True)
city_stats = city_stats.sort_values('season')

fig = go.Figure()
    
# Столбцы со средней температурой и станд. откл.
fig.add_trace(go.Bar(
    x=city_stats['season'],
    y=city_stats['season_city_mean'],
    name='Средняя температура',
    marker_color='#1f77b4',
    error_y=dict(
        type='data',
        array=city_stats['season_city_std'],
        visible=True,
        color='black',
        thickness=1.5,
        width=3
    )))
    
fig.update_layout(
    xaxis_title='Сезон',
    yaxis_title='Температура (C)',
    height=400,
    showlegend=False)

fig.update_xaxes(ticktext=seasons, tickvals=seasons)
    
st.plotly_chart(fig)

#=======================ДОПОЛНИТЕЛЬНЫЕ ГРАФИКИ НА БОНУС=======================================
st.subheader(f'Шаг 6: Гистограмма распределения температуры')

# Множественный выбор сезонов
selected_seasons = st.multiselect(
    'Выберите сезоны для отображения', 
    options=seasons,
    default=seasons,
    key='season_selector'
)

bins = st.slider('Количество интервалов (bins)', 5, 35, 20)

# Фильтруем данные по выбранным сезонам
dt_hist = hist_city[hist_city['season'].isin(selected_seasons)]['temperature']

# Создаем гистограмму с Plotly
fig = go.Figure()

# Добавляем гистограмму
fig.add_trace(go.Histogram(
    x=dt_hist,
    nbinsx=bins,
    marker_color='#ffad8f',
    opacity=0.8,
    name='Температура',
    hovertemplate='<b>Диапазон:</b> %{x}<br><b>Количество:</b> %{y}<extra></extra>'
))

# Настройка внешнего вида
fig.update_layout(
    xaxis=dict(
        title='Температура (C)',
        title_font=dict(size=14)
    ),
    yaxis=dict(
        title='Частота',
        title_font=dict(size=14)
    ),
    height=600,
    template='plotly_white',
    hovermode='x unified',
    showlegend=False,
    bargap=0.05
)

# Добавлим линию со средним значением температуры для наглядности
mean_temp = dt_hist.mean()
fig.add_vline(
    x=mean_temp, 
    line_dash='dash', 
    line_color='red',
    annotation_text=f'Среднее: {mean_temp:.1f}C',
    annotation_position='top right'
)

st.plotly_chart(fig)

# Ссылка на GitHub
with st.sidebar:
    st.markdown("---")
    st.markdown("**👩‍💻 Автор:** Сморчкова Юлиана")
    st.markdown("**🔗 Подробнее на** [GitHub](https://github.com/smorchkova001-git/weather-analysis-dashboard)")
    st.markdown("---")