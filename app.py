from flask import *
from flask_cors import CORS
import mysql.connector
import jwt
import requests
from datetime import datetime, timedelta
from mysql.connector import pooling
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder="public")
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.json.ensure_ascii = False
#####

CORS(app, resources={r"/api/*": {"origins": "*"}})

load_dotenv()
dbconfig = {
    "host": os.getenv("DB_HOST"),  
    "user": os.getenv("DB_USER"),  
    "password": os.getenv("DB_PASSWORD"), 
    "database": os.getenv("DB_DATABASE"),
}
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=32, **dbconfig)


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

        # 測試500錯誤 print(undefined_variable)

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
            count_query = "SELECT COUNT(*) FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id WHERE {} OR {}".format(
                mrt_query, attraction_query
            )
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
            query = "SELECT attraction.id, attraction.name, attraction.CAT, attraction.description, attraction.address, attraction.direction, mrt.name, attraction.latitude, attraction.longitude FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id WHERE {} OR {}  ORDER BY attraction.id LIMIT %s, 12".format(
                mrt_query, attraction_query
            )
            params = (*mrt_params, *attraction_params, start_index)

        else:
            query = "SELECT attraction.id, attraction.name, attraction.CAT, attraction.description, attraction.address, attraction.direction, mrt.name, attraction.latitude, attraction.longitude FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id   ORDER BY attraction.id  LIMIT %s, 12"
            params = (start_index,)
            # print(query)
        cursor.execute(query, params)
        attractions = cursor.fetchall()

        response_data = {"nextPage": next_page, "data": []}

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
                "images": [],
            }
            # print(attraction_data)
            # 查詢該景點的所有圖片並存入陣列
            images_query = "SELECT images FROM attractionimg WHERE attraction_id = %s"
            cursor.execute(images_query, (attraction[0],))  # 使用景點的 id 作為參數
            image_rows = cursor.fetchall()
            image_urls = [image_row[0] for image_row in image_rows]


            attraction_data["images"] = image_urls
            response_data["data"].append(attraction_data)

        response_json = json.dumps(response_data, ensure_ascii=False)
        cursor.close()

        return response_json

    except Exception as e:
        error_message = "伺服器內部錯誤：" + str(e)
        error_response = {"error": True, "message": error_message}

        return jsonify(error_response), 500
    finally:
        cursor.close()
        cnx.close()


@app.route("/api/attraction/<int:attractionId>", methods=["GET"])
def get_attraction_by_id(attractionId):
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        query = "SELECT attraction.id, attraction.name, attraction.CAT, attraction.description, attraction.address, attraction.direction, mrt.name, attraction.latitude, attraction.longitude FROM attraction INNER JOIN mrt ON attraction.MRT_ID = mrt.id WHERE attraction.id = %s"

        cursor.execute(query, (attractionId,))
        attraction = cursor.fetchone()

        if attraction is None:
            error_message = f"找不到編號為 {attractionId} 的景點資料"
            error_response = {"error": True, "message": error_message}
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
            "images": [],
        }

        images_query = "SELECT images FROM attractionimg WHERE attraction_id = %s"
        cursor.execute(images_query, (attractionId,))
        image_rows = cursor.fetchall()
        image_urls = [image_row[0] for image_row in image_rows]
        attraction_data["images"] = image_urls

        response_data = {"data": attraction_data}
        cursor.close()
        return jsonify(response_data)

    except Exception as e:

        error_message = "伺服器內部錯誤：" + str(e)
        error_response = {"error": True, "message": error_message}
        print(error_response)
        return jsonify(error_response), 500
    finally:

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
        response_data = {"data": mrt_names_list}
        cursor.close()
        return jsonify(response_data)
    except Exception as e:
        error_message = "伺服器內部錯誤：" + str(e)
        error_response = {"error": True, "message": error_message}
        return jsonify(error_response), 500
    finally:

        cursor.close()
        cnx.close()


@app.route("/api/user", methods=["POST"])
def signup():
    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()

    user = request.get_json()
    print("user:", user)

    inputName = user["name"]
    inputEmail = user["email"]
    inputPassword = user["password"]

    
    cursor.execute("SELECT email FROM members WHERE email= %s", (inputEmail,))
    result = cursor.fetchone()
    print("result", result)
    try:
        if result is not None:
            print("email已經註冊帳戶")
            error_message = "email已經註冊帳戶"
            error_response = {"error": True, "message": error_message}
            return jsonify(error_response), 400

        else:
            print("註冊成功")
            cursor.execute(
                "INSERT INTO members(name,email,password) VALUES(%s, %s , %s)",
                (inputName, inputEmail, inputPassword),
            )

            cnx.commit()
            return jsonify({"ok": True}), 200
    except Exception as e:
        return {"error": True, "message": str(e)}

    finally:

        cursor.close()
        cnx.close()


@app.route("/api/user/auth", methods=["PUT"])
def userLogin():
    key = os.getenv("key")

    cnx = cnxpool.get_connection()
    cursor = cnx.cursor()

    user = request.get_json()
    inputEmail = user["email"]
    inputPassword = user["password"]
    print("inputEmail:", inputEmail)
    print("inputPassword:", inputPassword)
    cursor.execute(
        "SELECT id,name,email,password FROM members WHERE  email=%s and password=%s;",
        (inputEmail, inputPassword),
    )
    result = cursor.fetchone()
    print("result", result)
    try:
        if result is not None:
            print("result is not None")
            print("result:", result)
            exptime = datetime.now() + timedelta(days=7)
            exp_timestemp = exptime.timestamp()
            payload = {
                "id": result[0],
                "name": result[1],
                "email": result[2],
                "exp": exp_timestemp,
            }
            token = jwt.encode(payload=payload, key=key, algorithm="HS256")

            response = jsonify({"token": token}), 200
            print("token:", token)
            print("response:", response)
            return response
        else:
            print("登入失敗")
            return jsonify({"error": True, "message": "帳號或密碼輸入錯誤"}), 400
    except Exception as e:
        return {"error": True, "message": str(e)}

    finally:
        cursor.close()
        cnx.close()


@app.route("/api/user/auth", methods=["GET"])
def getusersData():
    key = os.getenv("key")

    auth_header = request.headers.get("Authorization", None)
    try:
        if not auth_header:
            print("auth未登入的狀態")
            return jsonify({"data": None}), 200

        token = auth_header.split(" ")[1]
        print("auth已登入的狀態")
        payload = jwt.decode(token, key, algorithms="HS256")
        user_info = {
            "id": payload["id"],
            "name": payload["name"],
            "email": payload["email"],
        }

        return jsonify({"data": user_info}), 200

    except Exception as e:
        return {"error": True, "message": str(e)}



@app.route("/api/booking", methods=["GET"])
def getBooking():
    key = os.getenv("key")

    auth_header = request.headers.get("Authorization", None)
    try:
        if not auth_header:
            error_message = "未登入系統，拒絕存取"
            print(error_message)
            error_response = {"error": True, "message": error_message}
            return jsonify(error_response), 403
        else:
            print("已登入存取booking")
            print("booking_auth_header:", auth_header)
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, key, algorithms="HS256")
            memberid = payload["id"]
            print("booking_get_payload:", payload)

            cnx = cnxpool.get_connection()
            cursor = cnx.cursor()
            sql = "SELECT * FROM booking WHERE member_id= %s;"
            cursor.execute(sql, (memberid,))
            result = cursor.fetchone()
            print("booking_get_result:", result)
            if result == None:
                print("沒有訂單資料")
                response = jsonify({"data": None}), 200
                print("booking_get_result==none:", response)

                return response

            attractionId = result[2]
            print("attractionId:", attractionId)
            cursor.execute(
                "SELECT id, name, address FROM attraction WHERE id =%s;",
                (attractionId,),
            )
            att = cursor.fetchone()
            attraction = {
                "id": att[0],
                "name": att[1],
                "address": att[2],
                "image": [],
            }
            print("attraction_1:", attraction)
            images_query = "SELECT images FROM attractionimg WHERE attraction_id = %s"
            cursor.execute(images_query, (attractionId,))
            image_rows = cursor.fetchone()
            print("image_rows:", image_rows)
            attraction["image"] = image_rows[0]
            print("attraction_2:", attraction)
            data = {
                "attraction": attraction,
                "date": result[3].strftime("%Y-%m-%d"),
                "time": result[4],
                "price": int(result[5]),
            }
            print("data:", data)
            response = jsonify({"data": data}), 200
            print(response)
            return response
    except Exception as e:
        return {"error": True, "message": str(e)}



@app.route("/api/booking", methods=["POST"])
def creatBooking():
    key = os.getenv("key")

    auth_header = request.headers.get("Authorization", None)
    bookingdata = request.get_json()
    try:
        if not auth_header:
            error_message = "未登入系統，拒絕存取"
            error_response = {"error": True, "message": error_message}
            return jsonify(error_response), 403

        elif None in bookingdata:

            return jsonify({"error": True, "message": "請填寫完整資料"}), 400

        else:
            print("已登入存取booking")
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, key, algorithms="HS256")
            memberid = payload["id"]

            attractionId = bookingdata["attractionId"]
            date = bookingdata["date"]
            time = bookingdata["time"]
            price = bookingdata["price"]


            cnx = cnxpool.get_connection()
            cursor = cnx.cursor()
            sql = "SELECT * FROM booking WHERE member_id=%s;"
            cursor.execute(sql, (memberid,))
            bookingData = cursor.fetchone()

            if bookingData == None:
                sql = "INSERT INTO booking (member_id, attraction_id, date, time, price) VALUES(%s, %s, %s, %s, %s);"
                val = (memberid, attractionId, date, time, price)
            else:
                sql = "UPDATE booking SET member_id=%s, attraction_id=%s, date=%s, time=%s, price=%s WHERE member_id=%s;"
                val = (memberid, attractionId, date, time, price, memberid)
            cursor.execute(sql, val)
            cnx.commit()
            response = {"ok": True}


            return jsonify(response), 200

    except Exception as e:
        return {"error": True, "message": "伺服器內部錯誤" + str(e)}

    finally:
        cursor.close()
        cnx.close()


@app.route("/api/booking", methods=["DELETE"])
def deleteBooking():
    key = os.getenv("key")

    auth_header = request.headers.get("Authorization", None)
    try:
        if not auth_header:
            error_message = "未登入系統，拒絕存取"
            error_response = {"error": True, "message": error_message}
            return jsonify(error_response), 403
        else:
            print("這邊1")
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, key, algorithms="HS256")
            memberid = payload["id"]
            print("這邊2")
            cnx = cnxpool.get_connection()
            cursor = cnx.cursor()
            sql = "DELETE FROM booking WHERE member_id= %s;"
            cursor.execute(sql, (memberid,))
            cnx.commit()
            cursor.close()
            response = {"ok": True}
            return jsonify(response), 200


    except Exception as e:
        return {"error": True, "message": "伺服器內部錯誤" + str(e)}


@app.route("/api/orders", methods=["POST"])
def createorder():
    key = os.getenv("key")

    partner_key = os.getenv("partner_key")
    auth_header = request.headers.get("Authorization", None)
    try:
        if not auth_header:
            error_message = "未登入系統，拒絕存取"
            error_response = {"error": True, "message": error_message}
            return jsonify(error_response), 403

        else:
            print("已登入狀態送order_post到後端")
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, key, algorithms="HS256")
            memberid = payload["id"]
            print("memberid:", memberid)
            memberName = payload["name"]

            order = request.get_json()
            name = order["order"]["contact"]["name"]
            email = order["order"]["contact"]["email"]
            phone = order["order"]["contact"]["phone"]
            attraction_id = order["order"]["trip"]["attraction"]["id"]
            attraction_name = order["order"]["trip"]["attraction"]["name"]
            attraction_address = order["order"]["trip"]["attraction"]["address"]
            attraction_image = order["order"]["trip"]["attraction"]["image"]
            date = order["order"]["trip"]["date"]
            time = order["order"]["trip"]["time"]
            prime = order["prime"]
            price = order["order"]["price"]

            merchant_id = "li0502178_CTBC"
            print("partner_key:", partner_key)
            print("prime:", order["prime"])
            print(order)
            print("attraction_id:", attraction_id)
            print("date:", date)
            print("time:", time)
            print("price:", price)
            print("name:", name)
            print("email:", email)
            print("phone:", phone)
            current_time = datetime.now()
            order_number = current_time.strftime("%Y%m%d%H%M%S")
            print("order_number:", order_number)
            status = "未付款"
            cnx = cnxpool.get_connection()
            cursor = cnx.cursor()
            sql = """
                    INSERT INTO orders (
                        order_number, member_id, attraction_id,  date, time, price,
                        contact_name, contact_email, contact_phone, status) 
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
          
            val = (
                order_number,
                memberid,
                attraction_id,
                date,
                time,
                price,
                name,
                email,
                phone,
                status,
            )
            cursor.execute(sql, val)
            cnx.commit()
            SendToTapPayData = {
                "prime": prime,
                "partner_key": partner_key,
                "merchant_id": "li0502178_CTBC",
                "details": "TapPay Test",
                "amount": price,
                "cardholder": {"phone_number": phone, "name": name, "email": email},
                "remember": "false",
            }
            print(SendToTapPayData)
            url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
            headers = {"Content-Type": "application/json", "x-api-key": partner_key}
            response = requests.post(url, headers=headers, json=SendToTapPayData)
            print("response:", response)
            print("JSON Response ", response.json())
            print("status:", response.json()["status"])
            if response.json()["status"] == 0:
                print("status是0")
                status = "已付款"
                sql = "UPDATE orders SET status=%s WHERE order_number = %s;"
                val = (status, order_number)

                cursor.execute(sql, val)
                cnx.commit()

                response = {
                    "data": {
                        "number": order_number,
                        "payment": {"status": 0, "message": "付款成功"},
                    }
                }
                cursor.execute(
                        "DELETE FROM booking;")
                cnx.commit()
                return jsonify(response), 200
            else:
                response={
                    "error": "true",
                    "message": "訂單建立失敗，輸入不正確或其他原因"
                    }
                return jsonify(response), 400
            

    except Exception as e:
        return {"error": True, "message": "伺服器內部錯誤" + str(e)}

    finally:
        cursor.close()
        cnx.close()
@app.route("/api/orders/<orderNumber>", methods=["GET"])
def getorder(orderNumber):
    key = os.getenv("key")

    auth_header = request.headers.get("Authorization", None)
    print("orderNumber:",orderNumber)
    try:
        if not auth_header:
            error_message = "未登入系統，拒絕存取"
            error_response = {"error": True, "message": error_message}
            return jsonify(error_response), 403
        else:   
            print("已登入狀態送order_get到後端")

            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, key, algorithms="HS256")
            memberid = payload["id"]
            print("memberid:", memberid)
            memberName = payload["name"]   
            cnx = cnxpool.get_connection()
            cursor = cnx.cursor()
            sql="SELECT orders.order_number, orders.member_id, orders.attraction_id, orders.date, orders.time, orders.price, orders.contact_name, orders.contact_email, orders.contact_phone, orders.status, attraction.name, attraction.address FROM orders INNER JOIN attraction ON orders.attraction_id = attraction.id WHERE orders.order_number = %s;"
            val=(orderNumber,) 
            cursor.execute(sql, val)

            result= cursor.fetchone()
            if result==None:
                print("查無此訂單編號")
                return jsonify(result), 200


            attraction_Id=result[2]
            attraction_name=result[10]
            attraction_address=result[11]
            order_price=result[5]
            date=result[3].strftime("%Y-%m-%d")
            time=result[4]
            contact_name=result[6]
            contact_email=result[7]
            contact_phone=result[8]
            if result[9]=="已付款":
                status=1
            else:
                status=0    
            # print("status:",status)
            
            
            images_query = "SELECT images FROM attractionimg WHERE attraction_id = %s"
            cursor.execute(images_query, (attraction_Id,))
            image_rows = cursor.fetchone()
            # print("image_rows:", image_rows)
            res={
                "data": {
                    "number": orderNumber,
                    "price": order_price,
                    "trip": {
                    "attraction": {
                        "id": attraction_Id,
                        "name": attraction_name,
                        "address": attraction_address,
                        "image": image_rows[0]
                    },
                    "date": date,
                    "time": time
                    },
                    "contact": {
                    "name": contact_name,
                    "email": contact_email,
                    "phone": contact_phone
                    },
                    "status": status
                }
                }
            # print(res)

            return jsonify(res), 200
    except Exception as e:
        return {"error": True, "message": "伺服器內部錯誤" + str(e)}

   
        


app.run(host="0.0.0.0", port=3000)
