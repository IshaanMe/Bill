import streamlit as st
import json
import os

DATA_FILE = "customer_data.json"
DEFAULT_SPICES = ["Turmeric", "Chili", "Coriander", "Cumin"]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

st.set_page_config(page_title="Spice Billing App", layout="wide")
st.title("🌶️ Spice Billing Application")

tab1, tab2 = st.tabs(["🧾 Billing", "📝 Customer Registration"])

with tab1:
    st.header("🧾 Billing")

    if not data:
        st.warning("No customer data found. Please register a customer first.")
    else:
        customer_names = list(data.keys())
        selected_customer = st.selectbox("Select Customer", customer_names)

        if selected_customer:
            customer_info = data[selected_customer]
            st.write(f"**Address:** {customer_info['address']}")
            st.subheader("Enter quantity in kg for each spice:")

            total_amount = 0
            quantities = {}
            for spice, price_per_kg in customer_info["spices"].items():
                qty = st.number_input(f"{spice} @ ₹{price_per_kg}/kg", min_value=0.0, step=0.1, key=spice)
                quantities[spice] = qty
                total_amount += qty * price_per_kg

            if st.button("Generate Bill"):
                st.success(f"Total Amount: ₹{total_amount:.2f}")
                st.write("**Breakdown:**")
                for spice in quantities:
                    if quantities[spice] > 0:
                        st.write(f"- {spice}: {quantities[spice]} kg × ₹{customer_info['spices'][spice]} = ₹{quantities[spice] * customer_info['spices'][spice]:.2f}")

with tab2:
    st.header("📝 Customer Registration")

    with st.form("register_form"):
        name = st.text_input("Customer Name")
        address = st.text_area("Customer Address")

        st.subheader("Enter price per kg for each spice:")
        prices = {}
        for spice in DEFAULT_SPICES:
            price = st.number_input(f"{spice} Price (₹/kg)", min_value=0.0, step=0.1, key=f"reg_{spice}")
            prices[spice] = price

        submitted = st.form_submit_button("Register Customer")
        if submitted:
            if not name or not address:
                st.error("Please enter both name and address.")
            elif name in data:
                st.error("Customer already exists!")
            else:
                data[name] = {
                    "address": address,
                    "spices": prices
                }
                save_data(data)
                st.success(f"Customer '{name}' registered successfully!")
