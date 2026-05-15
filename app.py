import pymssql
from groq import Groq 
from flask import Flask, render_template, request, redirect, url_for

# DATABASE DETAILS
server = 'sdplserver.database.windows.net'
database = 'dme'
user_name = 'dmeadmin'
password = 'Agri@774Safe#14'

client = Groq(api_key="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")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    chat_history = []

    if request.method == "POST":
        # Handle the Reset/Home button
        if 'reset' in request.form:
            return redirect(url_for('home'))

        user_question = request.form.get("query")
        if not user_question:
            return render_template("index.html", chat_history=[])

        # AI PROMPT
        prompt = f"""
        You are a SQL query generator. Convert to ONLY a SQL Server SELECT query.
        STRICT: No markdown, no explanation, no ```sql.
        Table: Daily_Packing_Data
        Columns: Serial_Number, Record_Number, Machine_No, Date_of_Packing, Time_of_Packing, Location, Machine, SKU, Weight_of_Bag, OPT_Name, Time_Stamp
        Question: {user_question}
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )

            ai_query = response.choices[0].message.content.strip()
            ai_query = ai_query.replace("```sql", "").replace("```", "")

            now_connect = pymssql.connect(
                server=server, user=user_name, password=password, database=database
            )
            cursor = now_connect.cursor()
            cursor.execute(ai_query)

            result = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            now_connect.close()

            chat_history = [{
                "question": user_question,
                "result": result,
                "columns": columns
            }]

        except Exception as e:
            return f"Error: {e}"

    return render_template("index.html", chat_history=chat_history)

if __name__ == "__main__":
    app.run(debug=True)