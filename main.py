import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get database credentials from environment variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# Connect to MySQL
def connect_to_db():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
# trying out query
# mycursor=mydb.cursor()
# mycursor.execute("select * from menu")
# for i in mycursor:
#     print(i)

#creating streamlit app

# Display menu
def display_menu():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_name, price FROM menu")
    rows = cursor.fetchall()
    st.subheader("Menu")
    for row in rows:
        st.write(f"Item ID: {row[0]} | Item: {row[1]} | Price: ${row[2]}")
    cursor.close()
    conn.close()

# Add order
def place_order(item_id, quantity):
    conn = connect_to_db()
    cursor = conn.cursor()
    # Insert into orders table
    cursor.execute("INSERT INTO orders (item_id, quantity) VALUES (%s, %s)", (item_id, quantity))
    conn.commit()
    st.success(f"Order placed successfully for Item ID {item_id} with Quantity {quantity}")
    cursor.close()
    conn.close()

# Generate bill
def generate_bill(order_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Get order details
    cursor.execute("""
        SELECT m.item_name, m.price, o.quantity, (m.price * o.quantity) as total
        FROM orders o 
        JOIN menu m ON o.item_id = m.item_id
        WHERE o.order_id = %s
    """, (order_id,))
    order_details = cursor.fetchall()
    
    if order_details:
        st.subheader(f"Bill for Order ID: {order_id}")
        total_bill = 0
        for detail in order_details:
            st.write(f"Item: {detail[0]} | Price: ${detail[1]} | Quantity: {detail[2]} | Total: ${detail[3]}")
            total_bill += detail[3]

        # Insert into bills table
        cursor.execute("INSERT INTO bills (order_id, item_id, total_bill) VALUES (%s, %s, %s)", (order_id, order_details[0][0], total_bill))
        conn.commit()
        st.write(f"Total Bill: ${total_bill}")
        st.success("Bill generated successfully")
    else:
        st.error("Invalid Order ID")
    
    cursor.close()
    conn.close()

st.title("Canteen Management System")

# View Menu Section
if st.checkbox("View Menu"):
    display_menu()

# Place Order Section
st.subheader("Place an Order")
item_id = st.number_input("Enter Item ID", min_value=1)
quantity = st.number_input("Enter Quantity", min_value=1)
if st.button("Place Order"):
    place_order(item_id, quantity)

# Generate Bill Section
st.subheader("Generate Bill")
order_id = st.number_input("Enter Order ID to generate bill", min_value=1)
if st.button("Generate Bill"):
    generate_bill(order_id)