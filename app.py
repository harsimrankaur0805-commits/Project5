import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Telecom Analytics Dashboard",
    layout="wide",
    page_icon="📶"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.metric-box {
    background-color:#f8f9fa;
    padding:15px;
    border-radius:12px;
    text-align:center;
    box-shadow:2px 2px 8px rgba(0,0,0,0.05);
}
h1,h2,h3 {
    color:#1f2937;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("telecom_final_data.csv")

    df = df.rename(columns={
        "Total DL (Bytes)": "Total_DL",
        "Total UL (Bytes)": "Total_UL",
        "Satisfaction Score": "Satisfaction"
    })

    df["Total_DL_MB"] = df["Total_DL"] / (1024 * 1024)
    df["Total_UL_MB"] = df["Total_UL"] / (1024 * 1024)

    # Remove outliers
    df = df[df["Total_DL_MB"] < df["Total_DL_MB"].quantile(0.99)]
    df = df[df["Total_UL_MB"] < df["Total_UL_MB"].quantile(0.99)]

    # KMeans clustering
    # KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(df[["Total_DL_MB", "Total_UL_MB"]])

    df["Cluster"] = df["Cluster"].astype(str)

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Telecom Analytics")
section = st.sidebar.radio("Navigation", [
    "Overview",
    "User Distribution",
    "Data Usage",
    "Satisfaction"
])

cluster_filter = st.sidebar.selectbox(
    "Select Cluster",
    ["All"] + sorted(df["Cluster"].unique().tolist())
)

if cluster_filter != "All":
    df = df[df["Cluster"] == cluster_filter]

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>📶 Telecom User Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- OVERVIEW ----------------
if section == "Overview":

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Total Users", f"{len(df):,}")
    col2.metric("📥 Avg Download (MB)", round(df["Total_DL_MB"].mean(), 2))
    col3.metric("📤 Avg Upload (MB)", round(df["Total_UL_MB"].mean(), 2))
    col4.metric("😊 Avg Satisfaction (0-1)", round(df["Satisfaction"].mean(), 2))

    st.markdown("---")
    st.subheader("📌 Key Insights")

    if df["Total_DL_MB"].mean() > df["Total_UL_MB"].mean():
        st.info("📥 Users download more than upload → content-heavy usage.")

    if df["Satisfaction"].mean() < 0.3:
        st.warning("⚠️ Customer satisfaction is low → service improvements required.")

    col1, col2 = st.columns(2)

    cluster_counts = df["Cluster"].value_counts().reset_index()
    cluster_counts.columns = ["Cluster", "Users"]

    fig1 = px.bar(
        cluster_counts,
        x="Cluster",
        y="Users",
        color="Cluster",
        title="User Distribution by Cluster",
        text="Users"
    )

    fig2 = px.pie(
        cluster_counts,
        names="Cluster",
        values="Users",
        title="Cluster Market Share"
    )

    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

# ---------------- USER DISTRIBUTION ----------------
elif section == "User Distribution":

    st.subheader("📊 User Segmentation")

    cluster_counts = df["Cluster"].value_counts().reset_index()
    cluster_counts.columns = ["Cluster", "Users"]

    fig = px.bar(
        cluster_counts,
        x="Cluster",
        y="Users",
        color="Cluster",
        text="Users"
    )

    st.plotly_chart(fig, use_container_width=True)

    if cluster_counts["Users"].max() > cluster_counts["Users"].mean():
        st.warning("⚠️ One cluster dominates customer base.")

# ---------------- DATA USAGE ----------------
elif section == "Data Usage":

    st.subheader("📈 Data Consumption Patterns")

    col1, col2 = st.columns(2)

    fig1 = px.scatter(
        df.sample(min(5000, len(df))),
        x="Total_DL_MB",
        y="Total_UL_MB",
        color="Cluster",
        log_x=True,
        log_y=True,
        title="Download vs Upload Usage"
    )

    fig2 = px.histogram(
        df,
        x="Total_DL_MB",
        nbins=50,
        title="Download Usage Distribution"
    )

    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

    if df["Total_DL_MB"].max() > df["Total_DL_MB"].mean() * 5:
        st.warning("⚠️ Heavy users consume significantly high data.")

# ---------------- SATISFACTION ----------------
elif section == "Satisfaction":

    st.subheader("😊 Customer Satisfaction Analysis")

    col1, col2 = st.columns(2)

    fig1 = px.histogram(
        df,
        x="Satisfaction",
        nbins=25,
        title="Satisfaction Score Distribution"
    )

    fig2 = px.box(
        df,
        x="Cluster",
        y="Satisfaction",
        color="Cluster",
        title="Satisfaction by Cluster"
    )

    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

    if df["Satisfaction"].mean() < 0.3:
        st.warning("⚠️ Overall satisfaction is below expected level.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("📌 Built using Python, Streamlit, Plotly & Machine Learning")
        #cd "C:\Users\hp\OneDrive\Desktop\telecome project"
#python -m streamlit run app.py