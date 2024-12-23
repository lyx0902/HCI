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
    username = data.get('username')
    password = data.get('password')
    new_password = data.get('new_password')

    if not username or not password or not new_password:
        return jsonify({"message": "用户名、密码和新密码不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 验证当前密码
        query = "SELECT * FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and check_password(password, user['password']):
            # 更新密码
            new_hashed_password = encrypt_password(new_password)
            update_query = "UPDATE User SET password = %s WHERE username = %s"
            cursor.execute(update_query, (new_hashed_password, username))
            connection.commit()

            return jsonify({"message": "密码更新成功"}), 200
        else:
            return jsonify({"message": "用户名或密码错误"}), 401

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

# 插入新闻数据
# 插入新闻数据
@app.route('/add_article', methods=['POST'])
def add_article():
    data = request.get_json()
    atext = data.get('atext')

    if not atext:
        return jsonify({"message": "atext不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO Article (atext) VALUES (%s)"
        cursor.execute(query, (atext,))
        connection.commit()

        return jsonify({"message": "新闻数据插入成功"}), 201

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

# 读取新闻数据
@app.route('/get_article', methods=['GET'])
def get_article():
    data = request.get_json()
    aid = data.get('aid')

    if aid is None:
        return jsonify({"message": "aid不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM Article WHERE aid = %s"
        cursor.execute(query, (aid,))
        article = cursor.fetchone()

        if article:
            return jsonify({"article": article}), 200
        else:
            return jsonify({"message": "新闻数据不存在"}), 404

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

# 插入题目信息
@app.route('/add_problem', methods=['POST'])
def add_problem():
    data = request.get_json()
    ptext = data.get('ptext')
    A = data.get('A')
    B = data.get('B')
    C = data.get('C')
    D = data.get('D')
    answer = data.get('answer')

    if not ptext or not A or not B or not C or not D or not answer:
        return jsonify({"message": "所有字段均不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "INSERT INTO Problem (ptext, A, B, C, D, answer) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (ptext, A, B, C, D, answer))
        connection.commit()

        return jsonify({"message": "题目信息插入成功"}), 201

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

# 读取题目信息
@app.route('/get_problem', methods=['GET'])
def get_problem():
    data = request.get_json()
    pid =data.get('pid')

    if pid is None:
        return jsonify({"message": "pid不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM Problem WHERE pid = %s"
        cursor.execute(query, (pid,))
        problem = cursor.fetchone()

        if problem:
            return jsonify({"problem": problem}), 200
        else:
            return jsonify({"message": "题目信息不存在"}), 404

    except Error as e:
        return jsonify({"message": f"数据库错误: {str(e)}"}), 500
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.route('/add_points', methods=['PUT'])
def add_points():
    data = request.get_json()
    username = data.get('username')
    addpoint = data.get('addpoint')

    if not username or addpoint is None:
        return jsonify({"message": "用户名和加分数不能为空"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 获取当前的points
        query = "SELECT points FROM User WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            new_points = user['points'] + addpoint
            update_query = "UPDATE User SET points = %s WHERE username = %s"
            cursor.execute(update_query, (new_points, username))
            connection.commit()

            return jsonify({"message": "分数更新成功"}), 200
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
