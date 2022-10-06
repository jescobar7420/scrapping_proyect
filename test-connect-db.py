import psycopg2

def delete_row(cursor, connection, table, condition):
    try:
        query = """ DELETE FROM {} WHERE {}""".format(table, condition)
        cursor.execute(query)
        connection.commit()
        print("1 Record inserted successfully")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

try:
    connection = psycopg2.connect(user="postgres",
                                  password="123",
                                  host="localhost",
                                  port="5432",
                                  database="solomercados")

    cursor = connection.cursor()
    # Executing a SQL query to insert data into  table
    delete_row(cursor, connection, 'productos', 'id_producto = -1')
    # Fetch result
    cursor.execute("SELECT * FROM productos WHERE id_producto = -1")
    record = cursor.fetchall()
    print("Result ", record)

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

