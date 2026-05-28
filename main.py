from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import os
app=FastAPI()



# -------------------- CORS POLICY --------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],   # Allow all HTTP methods
    allow_headers=["*"]    # Allow all headers
)

conn_obj = mysql.connector.connect(
    host=os.getenv("db_host"),
    port=int(os.getenv("db_port")),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    database=os.getenv("db_name"),

)   
cursor_obj=conn_obj.cursor(dictionary=True)



cursor_obj.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn_obj.commit()


@app.post("/add_expense")
def add_expense__(new_data:dict):

    title=new_data["title"]
    amount=new_data["amount"]
    category=new_data["category"]

    query="""
    insert into expenses(title,amount,category)
    values(%s,%s,%s)
    """

    values=(title,amount,category)
    cursor_obj.execute(query,values)
    conn_obj.commit()

    return{
        "msg":f"{title} expense added successfully"
        
        }
@app.get("/get_expenses")
def get_expenses__():
    query="select * from expenses "
    
    cursor_obj.execute(query)
    data=cursor_obj.fetchall()
    
    return{
        "all_expenses":data
    }
    
@app.put("/update_expense/{expense_id}")
def update_expense__(
        expense_id: int,
        updated_data: dict
):

    query = """
    update expenses
    set title=%s,
        amount=%s,
        category=%s
    where expense_id=%s
    """

    values = (
        updated_data["title"],
        updated_data["amount"],
        updated_data["category"],
        expense_id
    )

    cursor_obj.execute(query, values)

    conn_obj.commit()

    return {
        "updated_msg":
        f"{expense_id} expense updated"
    }


@app.delete("/delete_expense/{expense_id}")
def delete_expense__(expense_id: int):

    query = """
    delete from expenses
    where expense_id=%s
    """

    values = (expense_id,)

    cursor_obj.execute(query, values)
    conn_obj.commit()

    return {
        "msg_delete": f"{expense_id} expense deleted"
    }
    
@app.get("/search_expense")
def search_expense__(category: str):

    query = """
    select *
    from expenses
    where category=%s
    """

    values = (category,)

    cursor_obj.execute(query, values)

    data = cursor_obj.fetchall()

    return {
        "search_results": data
    }

@app.get("/sort_expenses")
def sort_expenses__(sort_type: str):

    if sort_type == "price_desc":

        query = """
        select *
        from expenses
        order by amount desc
        """

    elif sort_type == "price_asc":

        query = """
        select *
        from expenses
        order by amount asc
        """

    elif sort_type == "date_desc":

        query = """
        select *
        from expenses
        order by created_at desc
        """

    else:

        query = """
        select *
        from expenses
        order by created_at asc
        """

    cursor_obj.execute(query)

    data = cursor_obj.fetchall()

    return {
        "sorted_expenses": data
    }

@app.get("/filter_expenses")
def filter_expenses__(
    min_amount: float,
    max_amount: float
):

    query = """
    SELECT *
    FROM expenses
    WHERE amount BETWEEN %s AND %s
    """

    values = (
        min_amount,
        max_amount
    )

    cursor_obj.execute(query, values)

    data = cursor_obj.fetchall()

    return {
        "filtered_expenses": data
    }
    
@app.get("/analyze_expenses")
def analyze_expenses__():

    # Total expense
    cursor_obj.execute("SELECT SUM(amount) as total FROM expenses")
    total = cursor_obj.fetchone()["total"]

    # Category wise expense
    cursor_obj.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        GROUP BY category
    """)
    category_data = cursor_obj.fetchall()

    # Average expense
    cursor_obj.execute("SELECT AVG(amount) as avg FROM expenses")
    avg = cursor_obj.fetchone()["avg"]

    return {
        "total_expense": total,
        "average_expense": avg,
        "category_wise": category_data
    }