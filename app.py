from flask import *
from flask_cors import CORS 
import mysql.connector
import jwt
from datetime import datetime, timedelta
from mysql.connector import pooling

app = Flask(__name__, 
            static_folder="public"
        )
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.json.ensure_ascii = False
#####

CORS(app, resources={r"/api/*": {"origins": "*"}})
# 連接到 MySQL 資料庫
# db_connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="1234",
#     database="webdb"
# )
# 創建資料庫游標
# cursor = db_connection.cursor()

#####
dbconfig = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'webdb'
}

cnxpool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10, 
    **dbconfig
)
# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

#####
# API - 取得景點資料列表
@app.route("/api/attractions", methods=["GET"])
def get_attractions():
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()    
        page = int(request.args.get("page", 0))
        keyword = request.args.get("keyword", None)

        #測試500錯誤 print(undefined_variable)

        # 計算資料的起始索引
        start_index = page * 12
        #####
        

        
        # API 處理程式碼 - 從資料庫取得景點資料總筆數

        if keyword:
            # 完全比對捷運站名稱
            mrt_query = "mrt.name = %s"
            mrt_params = (keyword,)
        
            # 模糊比對景點名稱
            attraction_query = "attraction.name LIKE %s"
            attraction_params = (f"%{keyword}%",)
        
            # 使用 OR 運算符結合兩個條件
            count_query = "SELECT COUNT(*) FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id WHERE {} OR {}".format(mrt_query, attraction_query)
            count_params = (*mrt_params, *attraction_params)
            # print("count_query:",count_query)
            # print("count_params:",count_params)
        else:
            count_query = "SELECT COUNT(*) FROM attraction"
            count_params = ()
        # cursor = db_connection.cursor()
        cursor.execute(count_query, count_params)
        total_records = cursor.fetchone()[0]
        # print("total_records:",total_records)
        # 計算總頁數
        total_pages = (total_records + 11) // 12
        # 假如目前頁數小於總頁數，表示還有下一頁
        has_next_page = page < (total_pages - 1)
        # print("page:",page)
        # print("has_next_page:",has_next_page)
        if has_next_page:
            next_page = page + 1
        else:
            next_page = None
        # 執行主要的查詢，取得景點資料
        if keyword:
            # 完全比對捷運站名稱
            mrt_query = "mrt.name = %s"
            mrt_params = (keyword,)
        
            # 模糊比對景點名稱
            attraction_query = "attraction.name LIKE %s"
            attraction_params = (f"%{keyword}%",)
        
            # 使用 OR 運算符結合兩個條件
            query = "SELECT attraction.id, attraction.name, attraction.CAT, attraction.description, attraction.address, attraction.direction, mrt.name, attraction.latitude, attraction.longitude FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id WHERE {} OR {}  ORDER BY attraction.id LIMIT %s, 12".format(mrt_query, attraction_query)
            params = (*mrt_params, *attraction_params, start_index)

        else:
            query = "SELECT attraction.id, attraction.name, attraction.CAT, attraction.description, attraction.address, attraction.direction, mrt.name, attraction.latitude, attraction.longitude FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id   ORDER BY attraction.id  LIMIT %s, 12"
            params = (start_index,)
            # print(query)
        cursor.execute(query, params)
        attractions = cursor.fetchall()
        
        
        response_data = {
            "nextPage": next_page,
            "data": []
        }
        
        for attraction in attractions:
            attraction_data = {
                "id": attraction[0],
                "name": attraction[1],
                "category": attraction[2],
                "description": attraction[3],
                "address": attraction[4],
                "transport": attraction[5],
                "mrt": attraction[6],
                "lat": attraction[7],
                "lng": attraction[8],
                "images": [] 
            }
            # print(attraction_data)
            # 查詢該景點的所有圖片並存入陣列
            images_query = "SELECT images FROM attractionimg WHERE attraction_id = %s"
            cursor.execute(images_query, (attraction[0],))  # 使用景點的 id 作為參數
            image_rows = cursor.fetchall()
            image_urls = [image_row[0] for image_row in image_rows]
        
            # 將圖片陣列加入景點資料
            attraction_data["images"] = image_urls
            response_data["data"].append(attraction_data)
        
        # 使用 json.dumps 轉換 JSON 物件為 JSON 字串
        response_json = json.dumps(response_data, ensure_ascii=False)
        cursor.close()
        # 回傳 JSON 字串
        return response_json


    except Exception as e:
        error_message = "伺服器內部錯誤：" + str(e)
        error_response = {
            "error": True,
            "message": error_message
        }

        return jsonify(error_response), 500
    finally:
        # print('finally')
        cursor.close()
        cnx.close()
@app.route("/api/attraction/<int:attractionId>", methods=["GET"])
def get_attraction_by_id(attractionId):
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        # 根據景點編號查詢資料庫，取得該景點的資料
        query = "SELECT attraction.id, attraction.name, attraction.CAT, attraction.description, attraction.address, attraction.direction, mrt.name, attraction.latitude, attraction.longitude FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id WHERE attraction.id = %s"
        # cursor = db_connection.cursor()
        cursor.execute(query, (attractionId,))
        attraction = cursor.fetchone()
        # print(undefined_variable)
        # 假如找不到該編號的景點資料，返回錯誤回應
        if attraction is None:
            error_message = f"找不到編號為 {attractionId} 的景點資料"
            error_response = {
                "error": True,
                "message": error_message
            }
            return jsonify(error_response), 400
        

        attraction_data = {
            "id": attraction[0],
            "name": attraction[1],
            "category": attraction[2],
            "description": attraction[3],
            "address": attraction[4],
            "transport": attraction[5],
            "mrt": attraction[6],
            "lat": attraction[7],
            "lng": attraction[8],
            "images": [] 
            }
        
        # 取得該景點的圖片網址陣列
        images_query = "SELECT images FROM attractionimg WHERE attraction_id = %s"
        cursor.execute(images_query, (attractionId,))
        image_rows = cursor.fetchall()
        image_urls = [image_row[0] for image_row in image_rows]
        # 將圖片陣列加入景點資料
        attraction_data["images"] = image_urls
        
        # # 將圖片網址陣列加入景點資料
        # attraction_data = {
        #     "id": attraction["id"],
        #     "name": attraction["name"],
        #     "category": attraction["category"],
        #     "description": attraction["description"],
        #     "address": attraction["address"],
        #     "transport": attraction["transport"],
        #     "mrt": attraction["mrt"],
        #     "lat": attraction["latitude"],
        #     "lng": attraction["longitude"],
        #     "images": image_urls
        # }
        
        # 返回景點資料
        response_data = {
            "data": attraction_data
        }
        # response_json = json.dumps(response_data, ensure_ascii=False)
        
        # # 回傳 JSON 字串
        # return response_json
        cursor.close()
        return jsonify(response_data)
        
    except Exception as e:
        # 捕捉其他例外錯誤
        error_message = "伺服器內部錯誤：" + str(e)
        error_response = {
            "error": True,
            "message": error_message
        }
        print(error_response)
        return jsonify(error_response), 500
    finally:
        # print('finally')
        cursor.close()
        cnx.close()

@app.route("/api/mrts", methods=["GET"])
def get_mrt_names_sorted_by_attractions():
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        # print(undefined_variable)
        # 查詢資料庫，計算每個捷運站的週邊景點數量
        query = """
           SELECT mrt.name, COUNT(attraction.MRT_ID) AS num_attractions
            FROM mrt
            INNER JOIN attraction ON mrt.id = attraction.MRT_ID AND mrt.name IS NOT NULL
            GROUP BY mrt.name
            ORDER BY num_attractions DESC;	
        """
        # cursor = db_connection.cursor()
        cursor.execute(query)
        mrt_rows = cursor.fetchall()
        
        # 將捷運站名稱提取出來，存入 mrt_names_list
        mrt_names_list = [mrt_row[0] for mrt_row in mrt_rows]
        
        # 回傳按照週邊景點數量排序的捷運站名稱列表
        response_data = {
            "data": mrt_names_list
        }
        cursor.close()
        return jsonify(response_data)
    except Exception as e:
        error_message = "伺服器內部錯誤：" + str(e)
        error_response = {
            "error": True,
            "message": error_message
        }
        return jsonify(error_response), 500
    finally:
        # print('finally')
        cursor.close()
        cnx.close()

@app.route("/api/user", methods=["POST"])
def signup():
    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()
    # cursor = db_connection.cursor()
    # data = request.data
    user = request.get_json()
    print("user:",user)
    # if 'name' not in user or 'email' not in user or 'password' not in user:
    #         return jsonify({"error": True, "message": "請填寫完整資訊"}), 400

    inputName = user["name"]
    inputEmail = user["email"]
    inputPassword = user["password"]
    
    # cursor.execute("SELECT name,email,password FROM members WHERE email= %s", (inputEmail,))
    cursor.execute("SELECT email FROM members WHERE email= %s", (inputEmail,))
    result=cursor.fetchone()
    print("result",result)
    try:
        if result is not None:
            print("email已經註冊帳戶")
            error_message ="email已經註冊帳戶"
            error_response = {
                "error": True,
                "message": error_message
            }
            return jsonify(error_response), 400
            
        else:
            print('註冊成功')
            cursor.execute("INSERT INTO members(name,email,password) VALUES(%s, %s , %s)", (inputName,inputEmail,inputPassword))
            # db_connection.commit()
            cnx.commit()
            return jsonify({ "ok":True }) ,200 
    except Exception as e:
        # return {"error": True, "message": str(e)}
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        # print('finally')
        cursor.close()
        cnx.close()


@app.route('/api/user/auth', methods=['PUT'])
def userLogin():
    key="qqqqqqqaz"
    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()
    # cursor = db_connection.cursor()
    user = request.get_json()
    inputEmail = user["email"]
    inputPassword = user["password"]
    print("inputEmail:",inputEmail)
    print("inputPassword:",inputPassword)
    cursor.execute("SELECT id,name,email,password FROM members WHERE  email=%s and password=%s;", (inputEmail, inputPassword))
    result = cursor.fetchone()
    print("result",result)
    try:
        if result is not None:
            print("result is not None")
            print("result:",result)
            exptime = datetime.now() + timedelta(days=7)
            exp_timestemp = exptime.timestamp()
            payload = {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'exp': exp_timestemp,
            }
            token = jwt.encode(payload=payload, key=key, algorithm="HS256")

            response =jsonify({"token": token}), 200
            print("token:",token)
            print("response:",response)
            return response
        else:
            print("登入失敗")
            return jsonify({"error": True, "message": "帳號或密碼輸入錯誤"}), 400
    except Exception as e:
        return {"error": True, "message": str(e)}
    finally:
        cursor.close()
        cnx.close()

@app.route('/api/user/auth', methods=['GET'])
def getusersData():
    key="qqqqqqqaz"
    auth_header = request.headers.get("Authorization", None)
    try:
        if (not auth_header):
            print("未登入的狀態")
            return jsonify({"data": None}), 200

        token = auth_header.split(" ")[1]
        print("已登入的狀態")
        payload=jwt.decode(token, key, algorithms="HS256")
        user_info = {
            "id": payload["id"],
            "name": payload["name"],
            "email": payload["email"]
        }
        print("user_info:",user_info)
        print("payload:",payload)
        return jsonify({"data": user_info}), 200

    except Exception as e:
        return {"error": True, "message": str(e)}

app.run(host="0.0.0.0", port=3000)