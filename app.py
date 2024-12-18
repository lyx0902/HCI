from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
from mysql.connector import Error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 数据库连接配置
def get_db_connection():
    return mysql.connector.connect(
        host="20.205.17.118",  # 数据库的 IP 地址
        user="root",      # 数据库用户名
        password="rootpassword",  # 数据库密码
        database="CarbonTrace"   # 数据库名称
    )

# 密码加密和验证
def encrypt_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# 用户登录接口l
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_password(password, user['password']):
            return jsonify({"message": "登录成功"}), 200
        else:
            return jsonify({"message": "用户名或密码错误"}), 401

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

# 用户注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('username')
    password = data.get('password')
    age = data.get('age')

    if not name or not password or age is None:
        return jsonify({"message": "用户名、密码和年龄不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM User WHERE username = %s"
        cursor.execute(query, (name,))
        user = cursor.fetchone()

        if user:
            return jsonify({"message": "用户名已存在"}), 400

        query = "INSERT INTO User (username, password, age) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, encrypt_password(password), age))
        connection.commit()

        return jsonify({"message": "注册成功"}), 201

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

# 用户信息更新接口
@app.route('/update_profile', methods=['PUT'])
def update_profile():
    data = request.get_json()
    name = data.get('username')
    new_name = data.get('new_name')
    new_password = data.get('new_password')
    new_age = data.get('new_age')
    hash_password = encrypt_password(new_password)

    if not name or not new_name or not new_age:
        return jsonify({"message": "用户名、新用户名和新年龄不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 更新用户名和邮箱
        update_query = "UPDATE User SET username = %s, password = %s, age = %s WHERE username = %s"
        cursor.execute(update_query, (new_name,hash_password, new_age,name))
        connection.commit()

        return jsonify({"message": "个人信息修改成功"}), 200

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/get_user_by_name', methods=['GET'])
def get_user_by_name():
    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({"message": "用户名不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            return jsonify({"user": user}), 200
        else:
            return jsonify({"message": "用户不存在"}), 404

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
