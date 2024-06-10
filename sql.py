import requests
import pyodbc  
from datetime import datetime, timedelta

# 1. Get Token (test1)
token_url = "https://tokenapi"
token_data = {
    "grant_type": "client_credentials",
    "client_id": "nKFnGuJC6scJsQ0Ken78JLdrILTXWcb7",
    "client_secret": "IGPzF00ayhgsiCimNFPGkzLCuf0UEnA5"
}

token_response = requests.post(token_url, data=token_data)

if token_response.status_code == 200:
    token = token_response.json().get("access_token")
    print("Token:", token)
else:
    print("Error getting token:", token_response.status_code, token_response.text)

# 2. Use Token to Get Data (test2)
data_url = "apixxx"
data_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}    
connection_config = 'DRIVER={SQL Server};' \
                        'SERVER=172.25.96.1;' \
                        'DATABASE=TimeDB;' \
                        'UID=sa;' \
                        'PWD=yourStrong(!)Password'

cnx = pyodbc.connect(connection_config)
cursor = cnx.cursor()

cursor.execute("SELECT empid FROM data_table2")
empid = [row.empid for row in cursor.fetchall()]

# กำหนด start_date และ end_date เป็นวันของเมื่อวาน
yesterday = datetime.now() - timedelta(days=7)
start_date = yesterday.strftime("%Y-%m-%d")
end_date = yesterday.strftime("%Y-%m-%d")
data_body = {
    "start_date": start_date,
    "end_date": end_date,
    "empid": empid
}


data_response = requests.post(data_url, headers=data_headers, json=data_body)

def insert_db(setid, empid, time_type, flags, time, locationname, lat, lng, created_time, updated_time):
    add_data_query = (
        "INSERT INTO data_table "
        "(setid, empid, time_type, flags, time, locationname, lat, lng, created_time, updated_time) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)"
    )

    cursor.execute(
        add_data_query,
        (setid, empid, time_type, flags, time, locationname, lat, lng, created_time, updated_time)
    )

    cnx.commit()

    # ปิดการเชื่อมต่อ


# ในกรณีที่ data_response.status_code เป็น 200
if data_response.status_code == 200:
    try:
        data = data_response.json()
        print("Data:", data)

        for record in data["data"]:
            insert_db(
                record["setid"], record["empid"], record["time_type"], record["flags"],
                record["time"], record["locationname"], record["lat"], record["lng"],
                record["created_time"], record["updated_time"]
            )

        print("Data inserted into the database.")
    except Exception as e:
        print("Error processing data:", str(e))
    finally:
        # ปิด cursor และ connection หลังจากประมวลผลข้อมูล
        cursor.close()
        cnx.close()
else:
    print("Error getting data:", data_response.status_code, data_response.text)