import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import streamlit as st
import os

sns.set(style='dark')

# ==============================
# DASHBOARD HEADER
# ==============================
# Mengatur judul dan layout
st.set_page_config(page_title="Bike Share Analysis Dashboard", layout="wide")

# Menentukan jalur file berdasarkan keberadaan file
data_file = "dashboard/df_day.csv" if os.path.isfile("dashboard/df_day.csv") else "df_day.csv"
image_file = "dashboard/rent bike.jpg" if os.path.isfile("dashboard/rent bike.jpg") else "rent bike.jpg"

# Memuat dataset
try:
    bike_data = pd.read_csv(data_file)
except FileNotFoundError:
    st.error("CSV file is missing. Please verify the path.")
    st.stop()

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("Informasi:")
st.sidebar.markdown("**• Nama: Zulfah Binti Toyibah**")
st.sidebar.markdown(
    "**• Email: [zulfahbintitoyibah6@gmail.com](zulfahbintitoyibah6@gmail.com)**")

# Mengubah kolom 'dteday' ke format tanggal
bike_data['dteday'] = pd.to_datetime(bike_data['dteday'])

# Mempersiapkan data
def get_monthly_rentals_summary(data):
    monthly_data = data.resample('M', on='dteday').agg({"cnt": "sum"}).reset_index()
    monthly_data['dteday'] = monthly_data['dteday'].dt.strftime('%b-%y')
    monthly_data.rename(columns={"dteday": "yearmonth", "cnt": "total_rentals"}, inplace=True)
    return monthly_data

def weekday_users_df(day_df):
    weekday_df = day_df.groupby("weekday").agg({"casual": "sum", "registered": "sum", "cnt": "sum"})
    weekday_df = weekday_df.reset_index()
    weekday_df.rename(columns={"cnt": "total_users", "casual": "casual_users", "registered": "registered_users"}, inplace=True)
    weekday_df = pd.melt(weekday_df, id_vars=['weekday'], value_vars=['casual_users', 'registered_users'], var_name='User Status', value_name='count_users')
    weekday_df['weekday'] = pd.Categorical(weekday_df['weekday'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    weekday_df = weekday_df.sort_values('weekday')
    return weekday_df

def get_seasonal_user_totals(data):
    # Select only numerical columns for aggregation
    season_totals = data.groupby("season")[['casual', 'registered', 'cnt']].sum().reset_index()
    season_totals = pd.melt(season_totals, id_vars=['season'], value_vars=['casual', 'registered'], var_name='user_type', value_name='total_users')
    season_totals['season'] = pd.Categorical(season_totals['season'], categories=['Spring', 'Summer', 'Fall', 'Winter'])
    return season_totals.sort_values('season')

# Filter data sidebar
start_date, end_date = bike_data["dteday"].min(), bike_data["dteday"].max()

with st.sidebar:
    st.image(image_file, width=275)
    st.sidebar.header("Filter Berdasarkan Rentang Tanggal:")
    selected_dates = st.date_input("Pilih Rentang Tanggal", [start_date, end_date], min_value=start_date, max_value=end_date)

# Validasi rentang tanggal yang dipilih
start_date, end_date = selected_dates if isinstance(selected_dates, list) and len(selected_dates) == 2 else (start_date, end_date)
filtered_bike_data = bike_data[(bike_data["dteday"] >= start_date) & (bike_data["dteday"] <= end_date)]

# Persiapkan data berdasarkan filter
monthly_rentals = get_monthly_rentals_summary(filtered_bike_data)
weekly_user_totals = weekday_users_df(filtered_bike_data)
seasonal_user_totals = get_seasonal_user_totals(filtered_bike_data)

# Tampilkan metrik utama
st.title("🚲 Dashboard Analisis Penyewaan Sepeda")
st.markdown("---")

# Membuat kolom untuk menampilkan metrik utama
col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan", value=filtered_bike_data['cnt'].sum())
col2.metric("Total Penyewaan Kasual", value=filtered_bike_data['casual'].sum())
col3.metric("Total Penyewaan Terdaftar", value=filtered_bike_data['registered'].sum())
st.markdown("---")


# Plot penyewaan berdasarkan hari dalam minggu
fig_weekday = px.bar(weekly_user_totals, x='weekday', y='count_users', color='User Status', barmode='group', color_discrete_sequence=["lightblue", "blue"], title="Penyewaan Sepeda Berdasarkan Hari")
fig_weekday.update_layout(xaxis_title='Hari dalam Minggu', yaxis_title='Total Pengguna', yaxis_tickformat='d')
st.plotly_chart(fig_weekday, use_container_width=True)

# Plot penyewaan bulanan
fig_monthly = px.area(monthly_rentals, x='yearmonth', y='total_rentals', color_discrete_sequence=["blue"], title="Penyewaan Bulanan")
fig_monthly.update_layout(xaxis_title='Bulan-Tahun', yaxis_title='Total Penyewaan', yaxis_tickformat='d')
st.plotly_chart(fig_monthly, use_container_width=True)

# Plot penyewaan berdasarkan musim
fig_season = px.line(seasonal_user_totals, x='season', y='total_users', color='user_type', markers=True, title="Penyewaan Sepeda Berdasarkan Musim")
fig_season.update_layout(xaxis_title='Musim', yaxis_title='Total Pengguna', yaxis_tickformat='d')
st.plotly_chart(fig_season, use_container_width=True)