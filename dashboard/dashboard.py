import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), 'main_data.csv')
    if not os.path.exists(path):
        path = 'main_data.csv'
    data = pd.read_csv(path)
    data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])
    return data

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Data")

min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

start_date = date_range[0] if len(date_range) == 2 else min_date
end_date = date_range[1] if len(date_range) == 2 else max_date

categories = sorted(df['product_category_name_english'].dropna().unique())
selected_categories = st.sidebar.multiselect("Kategori Produk", categories)

states = sorted(df['customer_state'].dropna().unique())
selected_states = st.sidebar.multiselect("Negara Bagian (State)", states)

# Apply filters
filtered_df = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) & 
    (df['order_purchase_timestamp'].dt.date <= end_date)
]

if selected_categories:
    filtered_df = filtered_df[filtered_df['product_category_name_english'].isin(selected_categories)]

if selected_states:
    filtered_df = filtered_df[filtered_df['customer_state'].isin(selected_states)]

if filtered_df.empty:
    st.warning("Tidak ada transaksi yang cocok dengan filter yang dipilih.")
    st.stop()

# Header & KPIs
st.title("E-Commerce Analytics Dashboard")
st.caption("Analisis performa produk, logistik pengiriman, demografi, dan segmentasi RFM")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", f"{filtered_df['order_id'].nunique():,}")
col2.metric("Total Revenue", f"R$ {filtered_df['price'].sum()/1e6:.2f} M")
col3.metric("Avg Rating", f"{filtered_df['review_score'].mean():.2f} / 5.0")
col4.metric("Unique Customers", f"{filtered_df['customer_unique_id'].nunique():,}")

st.divider()

# Analysis Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Performa Produk", 
    "Logistik & Review", 
    "Demografi Wilayah", 
    "Segmentasi RFM"
])

# 1. Product Performance
with tab1:
    st.subheader("Top Kategori Produk")
    col_a, col_b = st.columns(2)
    
    with col_a:
        top_qty = filtered_df['product_category_name_english'].value_counts().head(5)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x=top_qty.values, y=top_qty.index, palette='Blues_r', ax=ax)
        ax.set_title("Top 5 Kategori (Unit Terjual)", fontweight='bold')
        ax.set_xlabel("Unit")
        for i, v in enumerate(top_qty.values):
            ax.text(v + (max(top_qty.values) * 0.02), i, f"{v:,}", va='center', fontweight='bold', fontsize=9)
        st.pyplot(fig)
        
    with col_b:
        top_rev = filtered_df.groupby('product_category_name_english')['price'].sum().sort_values(ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x=top_rev.values / 1e3, y=top_rev.index, palette='Greens_r', ax=ax)
        ax.set_title("Top 5 Kategori (Revenue Ribu BRL)", fontweight='bold')
        ax.set_xlabel("Revenue (R$ Ribu)")
        for i, v in enumerate(top_rev.values / 1e3):
            ax.text(v + (max(top_rev.values / 1e3) * 0.02), i, f"R$ {v:,.1f}K", va='center', fontweight='bold', fontsize=9)
        st.pyplot(fig)

# 2. Logistics & Review
with tab2:
    st.subheader("Dampak Keterlambatan Pengiriman")
    col_c, col_d = st.columns(2)
    
    deliv_summary = filtered_df.groupby('delivery_status').agg(
        avg_score=('review_score', 'mean'),
        pct_star_1=('review_score', lambda x: (x == 1).mean() * 100),
        pct_star_5=('review_score', lambda x: (x == 5).mean() * 100)
    ).reset_index()
    
    with col_c:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(data=deliv_summary, x='delivery_status', y='avg_score', palette=['#e74c3c', '#2ecc71'], ax=ax)
        ax.set_title("Rata-rata Skor Review", fontweight='bold')
        ax.set_ylabel("Rating (1-5)")
        ax.set_ylim(0, 5)
        for i, row in deliv_summary.iterrows():
            ax.text(i, row['avg_score'] + 0.15, f"{row['avg_score']:.2f}", ha='center', fontweight='bold')
        st.pyplot(fig)
        
    with col_d:
        review_pct = deliv_summary.melt(
            id_vars='delivery_status', 
            value_vars=['pct_star_1', 'pct_star_5'], 
            var_name='Rating', 
            value_name='Persentase'
        )
        review_pct['Rating'] = review_pct['Rating'].map({'pct_star_1': 'Bintang 1', 'pct_star_5': 'Bintang 5'})
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(data=review_pct, x='delivery_status', y='Persentase', hue='Rating', palette=['#c0392b', '#27ae60'], ax=ax)
        ax.set_title("Proporsi Ulasan Bintang 1 vs 5 (%)", fontweight='bold')
        ax.set_ylim(0, 80)
        for p in ax.patches:
            h = p.get_height()
            if h > 0:
                ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h + 1), ha='center', fontweight='bold', fontsize=9)
        st.pyplot(fig)

# 3. Geospatial Demographics
with tab3:
    st.subheader("Konsentrasi Pelanggan per Negara Bagian")
    col_e, col_f = st.columns([2, 1])
    
    geo_df = filtered_df.groupby('customer_state').agg(
        total_customers=('customer_unique_id', 'nunique'),
        total_revenue=('price', 'sum')
    ).reset_index().sort_values(by='total_customers', ascending=False)
    
    with col_e:
        top10_geo = geo_df.head(10)
        fig, ax = plt.subplots(figsize=(10, 5.5))
        palette = ['#e67e22' if state == 'SP' else '#bdc3c7' for state in top10_geo['customer_state']]
        sns.barplot(data=top10_geo, x='total_customers', y='customer_state', palette=palette, ax=ax)
        ax.set_title("Top 10 State Berdasarkan Jumlah Pelanggan", fontweight='bold')
        ax.set_xlabel("Pelanggan Unik")
        for p in ax.patches:
            w = p.get_width()
            ax.annotate(f"{int(w):,}", (w + (top10_geo['total_customers'].max() * 0.02), p.get_y() + p.get_height() / 2.),
                        va='center', fontweight='bold', fontsize=9)
        st.pyplot(fig)
        
    with col_f:
        st.markdown("**Top 5 State:**")
        top5_geo_table = geo_df.head(5).copy()
        top5_geo_table.columns = ['State', 'Pelanggan', 'Revenue']
        top5_geo_table['Revenue'] = top5_geo_table['Revenue'].apply(lambda x: f"R$ {x:,.0f}")
        st.dataframe(top5_geo_table, use_container_width=True)

# 4. RFM Segmentation
with tab4:
    st.subheader("Segmentasi Pelanggan (RFM)")
    snapshot_date = filtered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = filtered_df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    col_g, col_h, col_i = st.columns(3)
    
    with col_g:
        top_rec = rfm.sort_values(by='recency', ascending=True).head(5)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=top_rec['recency'], y=top_rec['customer_id'].str[:8] + '...', palette='Blues_r', ax=ax)
        ax.set_title("Recency Terendah (Hari)", fontweight='bold')
        st.pyplot(fig)
        
    with col_h:
        top_freq = rfm.sort_values(by='frequency', ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=top_freq['frequency'], y=top_freq['customer_id'].str[:8] + '...', palette='Purples_r', ax=ax)
        ax.set_title("Frequency Tertinggi (Orders)", fontweight='bold')
        st.pyplot(fig)
        
    with col_i:
        top_mon = rfm.sort_values(by='monetary', ascending=False).head(5)
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=top_mon['monetary'], y=top_mon['customer_id'].str[:8] + '...', palette='YlOrBr_r', ax=ax)
        ax.set_title("Monetary Tertinggi (BRL)", fontweight='bold')
        st.pyplot(fig)