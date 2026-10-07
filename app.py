import streamlit as st
import pandas as pd

from database import connection, Customer
from reports import ReportManager


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Smart Inventory & Billing",
    page_icon="🛒",
    layout="wide"
)


# ============================================================
# OBJECTS
# ============================================================

customer_manager = Customer(connection)
report_manager = ReportManager(connection)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_customers():
    cursor = connection.cursor()

    cursor.execute("""
        SELECT customer_id, name, phone, email, address
        FROM customers
        ORDER BY customer_id
    """)

    data = cursor.fetchall()
    cursor.close()

    return data


def get_products():
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id, product_name, price, stock_quantity
        FROM products
        ORDER BY product_id
    """)

    data = cursor.fetchall()
    cursor.close()

    return data


def get_customer_name(customer_id):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM customers
        WHERE customer_id = %s
    """, (customer_id,))

    data = cursor.fetchone()
    cursor.close()

    if data:
        return data[0]

    return "Unknown Customer"


def get_product_details(product_id):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_name, price, stock_quantity
        FROM products
        WHERE product_id = %s
    """, (product_id,))

    data = cursor.fetchone()
    cursor.close()

    return data


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛒 Smart Inventory")
st.sidebar.write("Inventory & Billing System")

st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "👤 Add Customer",
        "🛍️ Purchase & Billing",
        "📊 Reports"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if menu == "🏠 Dashboard":

    st.title("🛒 Smart Inventory & Billing System")

    st.subheader("Dashboard")

    customers = get_customers()
    products = get_products()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Customers",
            len(customers)
        )

    with col2:
        st.metric(
            "Total Products",
            len(products)
        )

    low_stock = 0

    for product in products:
        if product[3] <= 30:
            low_stock += 1

    with col3:
        st.metric(
            "Low Stock Products",
            low_stock
        )

    st.divider()

    st.subheader("📦 Current Products")

    if products:

        product_df = pd.DataFrame(
            products,
            columns=[
                "Product ID",
                "Product Name",
                "Price",
                "Stock Quantity"
            ]
        )

        st.dataframe(
            product_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No products found.")


# ============================================================
# ADD CUSTOMER
# ============================================================

elif menu == "👤 Add Customer":

    st.title("👤 Customer Management")

    st.subheader("Add New Customer")

    with st.form("customer_form"):

        name = st.text_input(
            "Customer Name"
        )

        phone = st.text_input(
            "Phone Number"
        )

        email = st.text_input(
            "Email"
        )

        address = st.text_area(
            "Address"
        )

        submit_customer = st.form_submit_button(
            "➕ Add Customer"
        )

        if submit_customer:

            if not name or not phone or not email or not address:

                st.warning(
                    "Please fill all customer details."
                )

            else:

                try:

                    customer_manager.new_customer(
                        name,
                        phone,
                        email,
                        address
                    )

                    st.success(
                        "Customer added successfully!"
                    )

                except Exception as e:

                    connection.rollback()

                    st.error(
                        f"Customer could not be added: {e}"
                    )

    st.divider()

    st.subheader("👥 Existing Customers")

    customers = get_customers()

    if customers:

        customer_df = pd.DataFrame(
            customers,
            columns=[
                "Customer ID",
                "Name",
                "Phone",
                "Email",
                "Address"
            ]
        )

        st.dataframe(
            customer_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No customers found."
        )


# ============================================================
# PURCHASE & BILLING
# ============================================================

elif menu == "🛍️ Purchase & Billing":

    st.title("🛍️ Purchase & Billing")

    customers = get_customers()
    products = get_products()

    if not customers:

        st.warning(
            "First add a customer."
        )

    elif not products:

        st.warning(
            "No products available."
        )

    else:

        # ----------------------------------------------------
        # CUSTOMER SELECTION
        # ----------------------------------------------------

        st.subheader("1️⃣ Select Customer")

        customer_options = {
            f"{customer[0]} - {customer[1]}":
            customer[0]
            for customer in customers
        }

        selected_customer = st.selectbox(
            "Customer",
            list(customer_options.keys())
        )

        customer_id = customer_options[selected_customer]

        st.info(
            f"Selected Customer: {get_customer_name(customer_id)}"
        )

        # ----------------------------------------------------
        # PRODUCT SELECTION
        # ----------------------------------------------------

        st.subheader("2️⃣ Select Product")

        product_options = {
            f"{product[0]} - {product[1]}":
            product[0]
            for product in products
        }

        selected_product = st.selectbox(
            "Product",
            list(product_options.keys())
        )

        product_id = product_options[selected_product]

        product_data = get_product_details(product_id)

        product_name = product_data[0]
        price = product_data[1]
        stock = product_data[2]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Product",
                product_name
            )

        with col2:
            st.metric(
                "Price",
                f"₹{price}"
            )

        with col3:
            st.metric(
                "Available Stock",
                stock
            )

        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        st.subheader("3️⃣ Quantity")

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max(1, stock),
            value=1,
            step=1
        )

        estimated_amount = price * quantity

        st.write(
            f"Estimated Amount: **₹{estimated_amount:.2f}**"
        )

        # ----------------------------------------------------
        # PAYMENT
        # ----------------------------------------------------

        st.subheader("4️⃣ Payment")

        col1, col2 = st.columns(2)

        with col1:

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "UPI",
                    "Card",
                    "Net Banking"
                ]
            )

        with col2:

            payment_status = st.selectbox(
                "Payment Status",
                [
                    "Paid",
                    "Pending"
                ]
            )

        # ----------------------------------------------------
        # COMPLETE PURCHASE
        # ----------------------------------------------------

        st.divider()

        if st.button(
            "✅ Complete Purchase",
            use_container_width=True
        ):

            if quantity > stock:

                st.error(
                    "Not enough stock available."
                )

            else:

                try:

                    order_id = customer_manager.complete_purchase(
                        customer_id,
                        product_id,
                        quantity,
                        payment_method,
                        payment_status
                    )

                    st.success(
                        f"Purchase completed successfully! Order ID: {order_id}"
                    )

                    st.balloons()

                    st.write(
                        f"Customer: **{get_customer_name(customer_id)}**"
                    )

                    st.write(
                        f"Product: **{product_name}**"
                    )

                    st.write(
                        f"Quantity: **{quantity}**"
                    )

                    st.write(
                        f"Payment Method: **{payment_method}**"
                    )

                except Exception as e:

                    connection.rollback()

                    st.error(
                        f"Transaction failed: {e}"
                    )


# ============================================================
# REPORTS
# ============================================================

elif menu == "📊 Reports":

    st.title("📊 Reports & Analysis")

    report_type = st.selectbox(
        "Select Report",
        [
            "Customer Order Analysis",
            "Payment Method Report",
            "Low Stock Report",
            "Product Sales Report"
        ]
    )

    st.divider()

    # --------------------------------------------------------
    # CUSTOMER ORDER ANALYSIS
    # --------------------------------------------------------

    if report_type == "Customer Order Analysis":

        st.subheader(
            "👥 Customer Order Analysis"
        )

        try:

            result = report_manager.customer_order_analysis()

            if result:

                df = pd.DataFrame(
                    result,
                    columns=[
                        "Customer ID",
                        "Customer Name",
                        "Total Orders"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No customer order data available."
                )

        except Exception as e:

            st.error(
                f"Could not generate report: {e}"
            )

    # --------------------------------------------------------
    # PAYMENT METHOD REPORT
    # --------------------------------------------------------

    elif report_type == "Payment Method Report":

        st.subheader(
            "💳 Payment Method Report"
        )

        try:

            result = report_manager.payment_method_report()

            if result:

                df = pd.DataFrame(
                    result,
                    columns=[
                        "Payment Method",
                        "Total Payments"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.bar_chart(
                    df.set_index("Payment Method")
                )

            else:

                st.info(
                    "No payment data available."
                )

        except Exception as e:

            st.error(
                f"Could not generate report: {e}"
            )

    # --------------------------------------------------------
    # LOW STOCK REPORT
    # --------------------------------------------------------

    elif report_type == "Low Stock Report":

        st.subheader(
            "⚠️ Low Stock Products"
        )

        try:

            result = report_manager.low_stock_report()

            if result:

                df = pd.DataFrame(
                    result,
                    columns=[
                        "Product ID",
                        "Product Name",
                        "Stock Quantity"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "No low-stock products."
                )

        except Exception as e:

            st.error(
                f"Could not generate report: {e}"
            )

    # --------------------------------------------------------
    # PRODUCT SALES REPORT
    # --------------------------------------------------------

    elif report_type == "Product Sales Report":

        st.subheader(
            "📦 Product Sales Report"
        )

        try:

            result = report_manager.product_sales_report()

            if result:

                df = pd.DataFrame(
                    result,
                    columns=[
                        "Product ID",
                        "Product Name",
                        "Total Sales"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.bar_chart(
                    df.set_index("Product Name")[
                        ["Total Sales"]
                    ]
                )

            else:

                st.info(
                    "No product sales data available."
                )

        except Exception as e:

            st.error(
                f"Could not generate report: {e}"
            )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Smart Inventory & Billing System"
)

st.sidebar.caption(
    "Python + PostgreSQL + OOP + Streamlit"
)