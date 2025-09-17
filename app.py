import streamlit as st
import pandas as pd
import os

# ======== Load Data ========
excel_file = os.path.join(os.path.dirname(__file__), "data.xlsx")
try:
    df = pd.read_excel(excel_file)
except FileNotFoundError:
    st.error(f"File {excel_file} tidak ditemukan.")
    st.stop()
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca file Excel: {e}")
    st.stop()

# Bersihkan data
df = df[(df["MIN_25_rev"] != "#NULL!") & (df["MAX_25_rev"] != "#NULL!")]
df["MIN_25_rev"] = pd.to_numeric(df["MIN_25_rev"], errors="coerce")
df["MAX_25_rev"] = pd.to_numeric(df["MAX_25_rev"], errors="coerce")

# ======== Session State ========
if "selected_item" not in st.session_state:
    st.session_state.selected_item = df["NAMA"].iloc[0]
if "price" not in st.session_state:
    st.session_state.price = None
if "unit_value" not in st.session_state:
    st.session_state.unit_value = None

# ======== UI Layout ========
st.title("💹 Validasi Harga & Satuan Komoditas")

st.sidebar.header("🔎 Pilihan Komoditas")
# Pilih komoditas di sidebar
st.session_state.selected_item = st.sidebar.selectbox(
    "Pilih Nama Barang", df["NAMA"].unique(),
    index=list(df["NAMA"]).index(st.session_state.selected_item)
)

# Ambil data komoditas terpilih
item_row = df[df["NAMA"] == st.session_state.selected_item].iloc[0]
min_price, max_price = item_row["MIN_25_rev"], item_row["MAX_25_rev"]
valid_unit = item_row["SATUAN"]

st.markdown(
    f"### 🛒 **{st.session_state.selected_item}**  \n"
    f"Rentang Harga/Satuan: **{min_price} – {max_price} Rupiah per {valid_unit}**"
)

# ======== Sub Menu (Tab) ========
tab_price, tab_unit = st.tabs(["💰 Masukkan Harga", "⚖️ Masukkan Satuan"])

# ---- Tab Harga ----
with tab_price:
    st.info("Masukkan harga total, sistem akan merekomendasikan perkiraan rentang jumlah satuan.")
    price = st.number_input(
        "Harga Total (Rupiah)",
        min_value=0.0,
        step=100.0,
        value=st.session_state.price if st.session_state.price else 0.0,
        key="price_input"
    )
    if price > 0:
        st.session_state.price = price
        # Hitung perkiraan rentang satuan
        min_qty = price / max_price if max_price else 0
        max_qty = price / min_price if min_price else 0
        if min_price <= price <= max_price:
            st.success(f"Harga sesuai rentang satuan standar ({min_price} – {max_price} / {valid_unit}).")
        else:
            st.warning("Harga di luar rentang harga per satuan, tapi kami hitung estimasi jumlah satuan.")
        st.write(
            f"💡 **Rekomendasi Rentang Satuan:** {min_qty:.2f} – {max_qty:.2f} **{valid_unit}** "
            f"untuk harga total Rp{price:,.0f}"
        )

# ---- Tab Satuan ----
with tab_unit:
    st.info("Masukkan jumlah satuan, sistem akan menampilkan rentang harga total.")
    unit_val = st.number_input(
        f"Jumlah {valid_unit}",
        min_value=0.0,
        step=0.1,
        value=st.session_state.unit_value if st.session_state.unit_value else 0.0,
        key="unit_input"
    )
    if unit_val > 0:
        st.session_state.unit_value = unit_val
        # Hitung rentang harga total
        min_total = min_price * unit_val
        max_total = max_price * unit_val
        st.write(
            f"💡 **Rentang Harga Total yang Direkomendasikan:** "
            f"Rp{min_total:,.0f} – Rp{max_total:,.0f} "
            f"untuk {unit_val:.2f} {valid_unit}"
        )

# Tombol Reset
if st.sidebar.button("🔄 Reset"):
    st.session_state.price = None
    st.session_state.unit_value = None
    st.experimental_rerun()
