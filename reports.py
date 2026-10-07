class ReportManager:

    def __init__(self,connection):
        self.connection = connection


    def customer_order_analysis(self):
        cursor = self.connection.cursor()

        cursor.execute("""select c.customer_id , c.name , count(o.order_id)
                            from customers as c
                            join orders as o
                            on c.customer_id = o.customer_id
                            group by c.customer_id , c.name""")

        result = cursor.fetchall()
        cursor.close()
        return result


    def payment_method_report(self):
        cursor = self.connection.cursor()

        cursor.execute("""select payment_method , count(payment_id)
                            from payments
                            group by payment_method
                            order by count(payment_id) desc""")

        result = cursor.fetchall()
        cursor.close()
        return result


    def low_stock_report(self):
        cursor = self.connection.cursor()

        cursor.execute("""select product_id , product_name  , stock_quantity
                            from products 
                            where stock_quantity <=30
                            order by stock_quantity asc""")

        result = cursor.fetchall()
        cursor.close()
        return result


    def product_sales_report(self):
        cursor = self.connection.cursor()

        cursor.execute("""select p.product_id,p.product_name,sum(oi.quantity) as total_sales
                            from products as p
                            join order_items as oi
                            on p.product_id = oi.product_id
                            group by p.product_id , p.product_name
                            order by total_sales desc""")

        result = cursor.fetchall()
        cursor.close()
        return result
    

        