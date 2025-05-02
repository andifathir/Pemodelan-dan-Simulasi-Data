import psycopg2
from psycopg2 import sql

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="mydb",
    user="postgres",
    password="Test99",
    host="postgres",
    port="5432"
)
cur = conn.cursor()

# Step 1: Load data into staging.sales
cur.execute("TRUNCATE TABLE staging.sales;")
cur.execute("""
    INSERT INTO staging.sales
    SELECT 
        transaction_id,
        transactional_date,
        product_id,
        customer_id,
        payment,
        credit_card,
        loyalty_card,
        CAST(cost AS numeric),
        quantity,
        price
    FROM public.sales;
""")

# Step 2: Populate core.dim_payment
cur.execute("""
    INSERT INTO core.dim_payment (payment, loyalty_card)
    SELECT DISTINCT COALESCE(payment, 'cash'), loyalty_card
    FROM staging.sales s
    WHERE NOT EXISTS (
        SELECT 1 FROM core.dim_payment dp
        WHERE dp.payment = COALESCE(s.payment, 'cash') AND dp.loyalty_card = s.loyalty_card
    );
""")

# Step 3: Transform and load into core.sales
cur.execute("""
    INSERT INTO core.sales (
        transaction_id, transactional_date, transactional_date_fk, product_id, product_fk,
        customer_id, payment_fk, credit_card, cost, quantity, price, total_cost, total_price, profit
    )
    SELECT 
        s.transaction_id,
        s.transactional_date,
        EXTRACT(YEAR FROM s.transactional_date)::bigint * 10000 + 
        EXTRACT(MONTH FROM s.transactional_date) * 100 + 
        EXTRACT(DAY FROM s.transactional_date) AS transactional_date_fk,
        s.product_id,
        p.product_pk AS product_fk,
        s.customer_id,
        dp.payment_pk AS payment_fk,
        s.credit_card,
        s.cost,
        s.quantity,
        s.price,
        s.cost * s.quantity AS total_cost,
        s.price * s.quantity AS total_price,
        (s.price * s.quantity) - (s.cost * s.quantity) AS profit
    FROM staging.sales s
    LEFT JOIN core.dim_product p ON s.product_id = p.product_id
    LEFT JOIN core.dim_payment dp ON COALESCE(s.payment, 'cash') = dp.payment AND s.loyalty_card = dp.loyalty_card
    ON CONFLICT (transaction_id) DO NOTHING;
""")

# Commit and close
conn.commit()
cur.close()
conn.close()
print("Full ETL load completed successfully!")