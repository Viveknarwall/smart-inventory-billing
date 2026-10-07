import psycopg2
import traceback


import os
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

class Customer:
    def __init__(self,connection):
        self.connection = connection

    def new_customer(self,name,phone,email,address):
        cursor = self.connection.cursor()
        cursor.execute("""insert into customers(name,phone,email,address)
                            values(%s,%s,%s,%s)""",(name,phone,email,address))

        self.connection.commit()
        cursor.close()
        print("Customer Enrolled Sucessfully !!")


    def purchase_products(self,customer_id,product_id,quantity):
        cursor = self.connection.cursor()

        cursor.execute("""insert into orders(customer_id) 
                            values(%s)""",(customer_id,))

        cursor.execute("""
            Insert Into orders(customer_id)
            Values(%s)
            RETURNING order_id
        """, (customer_id,))
        
        order_id = cursor.fetchone()[0]
        
        
        cursor.execute("""select price, stock_quantity from products where product_id=%s""",(product_id,))
        data = cursor.fetchone() 

        if not data:
            print("Invalid Product")
            return

        unit_price = data[0]
        stock_quantity = data[1]
        new_stock_quantity = stock_quantity - quantity

      
        cursor.execute("""insert into order_items(order_id,product_id,quantity,unit_price)
                            values(%s,%s,%s,%s)""",(order_id,product_id,quantity,unit_price))

        cursor.execute("""update products
                            set stock_quantity = %s
                            where product_id = %s""",(new_stock_quantity,product_id))

        cursor.close()
        
        return order_id


    def customer_bill(self,order_id):
        cursor = self.connection.cursor()

        cursor.execute("""select sum(unit_price*quantity)
                            from order_items
                            where order_id=%s""",(order_id,))
        subtotal = cursor.fetchone()[0]

        cursor.execute("""
            insert into bills(order_id,subtotal,total_amount)
            values(%s,%s,%s)""", (order_id, subtotal, subtotal))

        cursor.execute("""select discount,tax from bills where order_id=%s""",(order_id,))
        data = cursor.fetchone()
        
        discount_rate = data[0]
        tax_rate = data[1]

        discount_amount = subtotal * discount_rate / 100
        after_discount = subtotal - discount_amount
        tax_amount = after_discount * tax_rate /100

        final_amount = after_discount + tax_amount

        cursor.execute("""update bills set total_amount=%s where order_id=%s""",(final_amount,order_id))
        cursor.close()

    def customer_payment(self, order_id, payment_method, payment_status):
        cursor = self.connection.cursor()
    
        cursor.execute("""select bill_id, total_amount from bills where order_id=%s""", (order_id,))
    
        bill_id, total_amount = cursor.fetchone()
    
        cursor.execute("""
            insert into payments
            (bill_id, payment_method, amount_paid, payment_status)
            values (%s,%s,%s,%s)
        """, (bill_id, payment_method, total_amount, payment_status))
    
        cursor.close()

    
    def complete_purchase(self,customer_id,product_id,quantity,payment_method,payment_status):
        try:
            order_id = self.purchase_products(customer_id,product_id,quantity)
    
            self.customer_bill(order_id)
    
            self.customer_payment(order_id,payment_method,payment_status)
    
            self.connection.commit()
            print("Transaction Completed Successfully")
    
        except Exception as e:
    
            self.connection.rollback()
            print("Transaction Failed:", e)


