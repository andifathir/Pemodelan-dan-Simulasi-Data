import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="mydb",
    user="postgres",
    password="Fuckingpassword99",
    host="postgres",
    port="5432"
)
cur = conn.cursor()

# Get last load date
cur.execute("SELECT last_load_date FROM etl_metadata WHERE table_name = 'sales'")
last_load_date = cur.fetchone()[0]

# Load new data into staging.sales
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
    FROM public.sales p
    WHERE p.transactional_date > %s
    ON CONFLICT (transaction_id) DO NOTHING;
""", (last_load_date,))

# Update dim_payment with new combinations
cur.execute("""
    INSERT INTO core.dim_payment (payment, loyalty_card)
    SELECT DISTINCT COALESCE(payment, 'cash'), loyalty_card
    FROM staging.sales s
    WHERE NOT EXISTS (
        SELECT 1 FROM core.dim_payment dp
        WHERE dp.payment = COALESCE(s.payment, 'cash') AND dp.loyalty_card = s.loyalty_card
    );
""")

# Fetch new records for core.sales
cur.execute(sql.SQL("""
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
    WHERE s.transactional_date > %s
"""), (last_load_date,))
new_records = cur.fetchall()

if new_records:
    # Insert new records
    insert_query = sql.SQL("""
        INSERT INTO core.sales (
            transaction_id, transactional_date, transactional_date_fk, product_id, product_fk,
            customer_id, payment_fk, credit_card, cost, quantity, price, total_cost, total_price, profit
        ) VALUES %s
        ON CONFLICT (transaction_id) DO NOTHING
    """)
    execute_values(cur, insert_query, new_records)

    # Update last_load_date
    cur.execute("SELECT MAX(transactional_date) FROM staging.sales WHERE transactional_date > %s", (last_load_date,))
    new_last_load_date = cur.fetchone()[0]
    if new_last_load_date:
        cur.execute("UPDATE etl_metadata SET last_load_date = %s WHERE table_name = 'sales'", (new_last_load_date,))

# Commit and close
conn.commit()
cur.close()
conn.close()
print("Incremental ETL load completed successfully!")