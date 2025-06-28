import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

DATA_FILE = "customer_data.json"
SPICE_FILE = "spices.json"
PAYMENT_FILE = "payments.json"
ADMIN_PASSWORD = "admin123"  # Change for security

# ---------- Data Loaders ----------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    else:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

customer_data = load_json(DATA_FILE, {})
spice_list = load_json(SPICE_FILE, ["Turmeric", "Chili", "Coriander", "Cumin"])
payment_data = load_json(PAYMENT_FILE, {})

# ---------- Streamlit Setup ----------
st.set_page_config(page_title="Spice Billing App", layout="wide")
st.title(" Sai Sai Spices Billing Application 🌶️")

tab1, tab2, tab3, tab4 = st.tabs([
    "🧾 Billing", 
    "📝 Customer Registration", 
    "🛠️ Edit Customers/Spices", 
    "💳 Payments"
])

# ---------- Billing ----------
with tab1:
    st.header("🧾 Billing")

    if not customer_data:
        st.warning("No customer data found.")
    else:
        customer_names = list(customer_data.keys())
        selected_customer = st.selectbox("Select Customer", customer_names)

        if selected_customer:
            cust_info = customer_data[selected_customer]
            st.write(f"**Address:** {cust_info['address']}")
            st.subheader("Enter quantity (kg) for each spice:")

            total = 0
            order_details = {}
            for spice, price in cust_info["spices"].items():
                qty = st.number_input(f"{spice} @ ₹{price}/kg", 0.0, 100.0, 0.0, 0.1, key=spice)
                if qty > 0:
                    order_details[spice] = {"qty": qty, "price": price}
                    total += qty * price

            amount_received = st.number_input("Amount Received", 0.0, total, total, 0.1)
            due = total - amount_received
            date = st.date_input("Transaction Date", datetime.now())

            if st.button("Generate Bill"):
                st.success(f"Total Amount: ₹{total:.2f}")
                st.write("**Invoice Breakdown:**")
                for spice, detail in order_details.items():
                    st.write(f"- {spice}: {detail['qty']} kg × ₹{detail['price']} = ₹{detail['qty'] * detail['price']:.2f}")

                st.write(f"**Amount Received:** ₹{amount_received:.2f}")
                st.write(f"**Due Amount:** ₹{due:.2f}")

                # Save payment record
                if selected_customer not in payment_data:
                    payment_data[selected_customer] = []
                payment_data[selected_customer].append({
                    "date": str(date),
                    "total": total,
                    "received": amount_received,
                    "due": due,
                    "details": order_details
                })
                save_json(PAYMENT_FILE, payment_data)

                # Export CSV
                csv_data = pd.DataFrame([
                    {"Spice": k, "Qty": v["qty"], "Rate": v["price"], "Subtotal": v["qty"] * v["price"]}
                    for k, v in order_details.items()
                ])
                csv = csv_data.to_csv(index=False).encode("utf-8")
                st.download_button("Download Invoice as CSV", csv, "invoice.csv", "text/csv")

# ---------- Customer Registration ----------
with tab2:
    st.header("📝 Register New Customer")

    with st.form("reg_form"):
        name = st.text_input("Customer Name")
        address = st.text_area("Customer Address")

        spice_prices = {}
        st.subheader("Set spice-wise price (₹/kg):")
        for spice in spice_list:
            price = st.number_input(f"{spice} Price", min_value=0.0, step=0.1, key=f"reg_{spice}")
            spice_prices[spice] = price

        submit = st.form_submit_button("Register")
        if submit:
            if not name or not address:
                st.error("Please fill all fields.")
            elif name in customer_data:
                st.error("Customer already exists.")
            else:
                customer_data[name] = {
                    "address": address,
                    "spices": spice_prices
                }
                save_json(DATA_FILE, customer_data)
                st.success(f"{name} added successfully!")

# ---------- Edit Customers / Add Spices ----------
with tab3:
    st.header("🔐 Admin Area (Edit Customers & Spices)")

    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd == ADMIN_PASSWORD:
        # Add new spice
        new_spice = st.text_input("Add New Spice Name")
        if st.button("Add Spice"):
            if new_spice and new_spice not in spice_list:
                spice_list.append(new_spice)
                save_json(SPICE_FILE, spice_list)
                st.success(f"{new_spice} added to spice list.")
            else:
                st.warning("Spice already exists or is empty.")

        # Edit prices per customer
        st.subheader("Edit Customer Prices")
        cust = st.selectbox("Choose Customer", list(customer_data.keys()))
        if cust:
            for spice in spice_list:
                current = customer_data[cust]["spices"].get(spice, 0.0)
                new_price = st.number_input(f"{spice} price for {cust}", 0.0, 1000.0, current, 0.1, key=f"{cust}_{spice}")
                customer_data[cust]["spices"][spice] = new_price
            if st.button("Save Prices"):
                save_json(DATA_FILE, customer_data)
                st.success("Prices updated.")

    else:
        st.info("Enter admin password to unlock this section.")

# ---------- Payments and History ----------
with tab4:
    st.header("📊 Payment History")

    if not payment_data:
        st.info("No payment records yet.")
    else:
        cust = st.selectbox("Select Customer", list(payment_data.keys()), key="pay_cust")
        records = payment_data[cust]
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        st.dataframe(df[["date", "total", "received", "due"]].sort_values("date", ascending=False))

        total_received = df["received"].sum()
        total_due = df["due"].sum()
        st.metric("Total Received", f"₹{total_received:.2f}")
        st.metric("Total Due", f"₹{total_due:.2f}")
