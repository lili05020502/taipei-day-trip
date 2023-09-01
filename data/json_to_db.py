import json
import mysql.connector

# 連接到 MySQL 資料庫
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="webdb"
)

# 創建資料庫游標
cursor = db_connection.cursor()

# # 讀取 JSON 檔案
with open("taipei-attractions.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
    attractions = data["result"]["results"]

# ------------------------

# for attraction in attractions:
#     # ...（前面的 MRT 處理部分保持不變）
    
#     # 處理景點圖片
#     images = attraction["file"].split("https://")
#     image_urls = [f"https://{image}" for image in images[1:] if image.lower().endswith((".jpg", ".png"))]
#     print(image_urls)
#     if image_urls:
#         # 將景點 ID 插入到 attractionImg 資料表中的 attraction_id 欄位
#         attraction_id = cursor.lastrowid

#         # 將圖片連結插入到 attractionImg 資料表中的 images 欄位
#         insert_image_query = "INSERT INTO attractionImg (attraction_id, images) VALUES (%s, %s)"
#         for image_url in image_urls:
#             cursor.execute(insert_image_query, (attraction_id, image_url))
#             db_connection.commit()

# ------------------------
# 處理 MRT 資訊並插入到資料庫
for attraction in attractions:
    mrt_name = attraction["MRT"]
    
    # 檢查 MRT 名稱是否已存在於 mrt 資料表中
    select_mrt_query = "SELECT id FROM mrt WHERE name = %s"
    cursor.execute(select_mrt_query, (mrt_name,))
    mrt_id = cursor.fetchone()
    
    if mrt_id is None:
        # 如果 MRT 名稱不存在，則插入新的 MRT 資料
        insert_mrt_query = "INSERT INTO mrt (name) VALUES (%s)"
        cursor.execute(insert_mrt_query, (mrt_name,))
        db_connection.commit()
        mrt_id = cursor.lastrowid
        # print(mrt_id)
    else:
        mrt_id = mrt_id[0]
        # print(mrt_id)
    # 將資料插入 attraction 資料表，包括 MRT_ID
    insert_attraction_query = """
    INSERT INTO attraction (rate, direction, name, date, longitude, REF_WP, avBegin, langinfo, MRT_ID, 
    SERIAL_NO, RowNumber, CAT, MEMO_TIME, POI, idpt, latitude, description, _id, avEnd, address)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data_tuple = (attraction["rate"], attraction["direction"], attraction["name"], attraction["date"],
                  attraction["longitude"], attraction["REF_WP"], attraction["avBegin"], attraction["langinfo"],
                  mrt_id, attraction["SERIAL_NO"], attraction["RowNumber"], attraction["CAT"],
                  attraction["MEMO_TIME"], attraction["POI"], attraction["idpt"],
                  attraction["latitude"], attraction["description"], attraction["_id"], attraction["avEnd"],
                  attraction["address"])
    # print(data_tuple)
    cursor.execute(insert_attraction_query, data_tuple)
    db_connection.commit()

    # 處理景點圖片
    images = attraction["file"].split("https://")
    image_urls = [f"https://{image}" for image in images[1:] if image.lower().endswith((".jpg",".png"))]
    # print(image_urls)
    if image_urls:
        # 將景點 ID 插入到 attractionImg 資料表中的 attraction_id 欄位
        attraction_id = cursor.lastrowid

        # 將圖片連結插入到 attractionImg 資料表中的 images 欄位
        insert_image_query = "INSERT INTO attractionImg (attraction_id, images) VALUES (%s, %s)"
        for image_url in image_urls:
            cursor.execute(insert_image_query, (attraction_id, image_url))
            db_connection.commit()

# 關閉資料庫連接
cursor.close()
db_connection.close()

print("資料匯入完成")
