from flask import Flask, request, jsonify
import requests
import logging
from flask_sqlalchemy import SQLAlchemy
from flask import session
import os
from datetime  import datetime
import pytz
from flask_cors import CORS# CORSを有効にするために必要 リクエストを許可するために必要
from flask import render_template
from flask_login import LoginManager, UserMixin,login_user,logout_user,login_required #login用
from werkzeug.security import generate_password_hash, check_password_hash #login用ハッシュ
from flask_login import current_user#セッションからユーザー情報を取得するために必要

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"]) #CORSを有効にする.セッションを有効にするためにsupports_credentials=Trueを指定

#login用
login_manager = LoginManager()
login_manager.init_app(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-very-secret-key'  # 固定値に変更
#ローカルのセッション
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # ローカル開発時はFalse
app.config['SESSION_COOKIE_NAME'] = 'session'
db = SQLAlchemy(app)
#設定

#DB定義
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),  nullable=False)
    folder = db.Column(db.String(150),  nullable=False)
    question = db.Column(db.String(150), nullable=False)
    answer = db.Column(db.String(150), nullable=False)
    ydata = db.Column(db.String(150), nullable=True)
    date = db.Column(db.String(150), nullable=True)
    created_at= db.Column(db.DateTime, nullable=False,default=datetime.now(pytz.timezone('Asia/Tokyo')))
    def to_dict(self):
            return {
                
            }

#login用
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=False, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),  nullable=False)
    folder = db.Column(db.String(150),  nullable=False)
    created_at= db.Column(db.DateTime, nullable=False,default=datetime.now(pytz.timezone('Asia/Tokyo')))

class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),  nullable=False)
    date = db.Column(db.String(150),  nullable=False)
    time = db.Column(db.String(150),  nullable=False)
    created_at= db.Column(db.DateTime, nullable=False,default=datetime.now(pytz.timezone('Asia/Tokyo')))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #有効なセッションがある場合にユーザーを取得

@app.route('/account/loginnow', methods=['GET'])
def login_now():
     print("Session:", session)
     if current_user.is_authenticated:
        print(current_user.email)
        return jsonify({'msg': 'yes'}), 200
     print('not login')      
     return jsonify({'msg': 'no'}), 200       

@app.route('/account/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('name')
    email = data.get('mail')
    password = data.get('pas')

    user=User.query.filter_by(email=email).first() #メールアドレスが既に登録されているか確認
    if user:
        return jsonify({'msg': 'no'}), 400
    # パスワードをハッシュ化
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    new_user = User(email=email,username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'ok'}), 201

@app.route('/account/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('mail')
    password = data.get('pas')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password): #check_password_hash(db.password, password):
        # ログイン成功
        login_user(user)  # Flask-Loginを使用してユーザーをログインさせる
        return jsonify({'msg': 'ok'}), 200 #セッションも送られる
    else:
        # ログイン失敗
        return jsonify({'msg': 'no'}), 401

@app.route('/account/logout', methods=['GET'])
@login_required #セッションが有効な場合のみアクセス可能
def logout():
    print("logout called")  # ログ出力
    logout_user() # Flask-Loginを使用してユーザーをログアウトさせる
    return jsonify({'msg': 'ok'}), 200

@app.route('/timer', methods=['POST'])
def time():
    date= request.json.get('date')
    time = request.json.get('time')
    if current_user.is_authenticated:
        email=current_user.email
        time= Time(time=time,date=date,email=email)
        db.session.add(time)
        db.session.commit()
        return jsonify({'msg': 'ok'}), 200
    else:
        return jsonify({'msg': 'no'}), 200
@app.route('/timer', methods=['GET'])
def get_time():
    if current_user.is_authenticated:
        email=current_user.email
        times = Time.query.filter_by(email=email).all()
        timelist = []
        datelist = []

        for t in times:
            timelist.append(t.time)
            datelist.append(t.date)
        
        return jsonify({"time":timelist,"date":datelist}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
@app.route('/learn/makecard', methods=['POST'])
def create_card():
    data = request.get_json()
   
    fid = data.get('fid')
    folder = Folder.query.filter_by(id=fid).first()
    question = data.get('question')
    answer = data.get('answer')
    email = current_user.email 
    folder = folder.folder if folder else None  # フォルダが存在しない場合はNoneに設定
    cardexists = Card.query.filter_by(email=email, folder=folder,question=question).first()
    if cardexists:
        return jsonify({'msg': 'exist'}), 200
    card =Card(email=email, folder=folder, question=question, answer=answer)
    db.session.add(card)
    db.session.commit()

    
    return jsonify({'msg': 'ok'}), 201
   

@app.route('/learn/folder', methods=['POST'])
def create_folder():
    data = request.get_json()
    folder = data.get('folder')
    email = current_user.email
    folderexists = Folder.query.filter_by(email=email, folder=folder).first()
    if folderexists:
        return jsonify({'msg': 'exist'}), 200
    new_folder = Folder(email=email, folder=folder)
    db.session.add(new_folder)
    db.session.commit()
    
    return jsonify({'msg': 'ok'}), 201
@app.route('/learn/getfolder', methods=['GET'])
def get_folders():
    if current_user.is_authenticated:
        email = current_user.email
        folders = Folder.query.filter_by(email=email).all()
        folder_list = []
        ids = []
        for f in folders:
            folder_list.append(f.folder)
            ids.append(f.id)
            
        return jsonify({'folder': folder_list,"id":ids}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
@app.route('/learn/getall', methods=['POST'])
def get_allcard():
    if current_user.is_authenticated:
        email = current_user.email
        id = request.json.get('id')
        folder = Folder.query.filter_by(id=id).first().folder
        card = Card.query.filter_by(email=email, folder=folder).all()
        card_question = []
        card_answer = []
        
        ids = []
        for c in card:
            card_question.append(c.question)
            ids.append(c.id)
            card_answer.append(c.answer)
            
        return jsonify({'question': card_question,"answer":card_answer,"id":ids}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
#30件取得
@app.route('/learn/get', methods=['POST'])
def get_card30():
    if current_user.is_authenticated:
        email = current_user.email
        id = request.json.get('id')
        folder_obj = Folder.query.filter_by(id=id).first()
        if not folder_obj:
            return jsonify({'msg': 'folder not found'}), 404
        folder = folder_obj.folder
        cards = Card.query.filter_by(folder=folder, email=email).all()
        today = datetime.now().strftime('%Y%m%d')

        # フラグ付き比較関数
        def sort_key(card):
            is_empty = (not card.date or card.date == '') and (not card.ydata or card.ydata == '')
            # is_emptyがTrueなら(0, ...)、Falseなら(1, ...)
            return (0 if is_empty else 1, str(card.date or '') + str(card.ydata or '') + today)

        # バブルソート
        n = len(cards)
        for i in range(n):
            for j in range(0, n - i - 1):
                if sort_key(cards[j]) > sort_key(cards[j + 1]):
                    cards[j], cards[j + 1] = cards[j + 1], cards[j]
        if len(cards) > 10:
            cardre=cards[:10]
        else:
            cardre=cards
        if cardre:
            
            return jsonify({
                'question': [c.question for c in cardre],
                'answer': [c.answer for c in cardre],
                'id': [c.id for c in cardre]
            }), 200
        else:
            return jsonify({'msg': 'no'}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
@app.route('/learn/in', methods=['POST'])
def card_in():
    if current_user.is_authenticated:
        email = current_user.email
        id = request.json.get('card_id')
        ydata = request.json.get('ydata')
        date= datetime.now().strftime('%Y%m%d')
        card = Card.query.filter_by(id=id, email=email).first()
        if not card:
            return jsonify({'msg': 'no'}), 200
        card.ydata = ydata
        card.date = date
        db.session.commit()
        return jsonify({'msg': 'ok'}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
@app.route('/learn/delete', methods=['POST'])
def delete_card():
    if current_user.is_authenticated:
        email = current_user.email
        id = request.json.get('card_id')
        card = Card.query.filter_by(id=id, email=email).first()
        if not card:
            return jsonify({'msg': 'no'}), 200
        db.session.delete(card)
        db.session.commit()
        return jsonify({'msg': 'ok'}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
@app.route('/learn/editcard', methods=['POST'])
def edit_card():
    if current_user.is_authenticated:
        email = current_user.email
        id = request.json.get('card_id')
        question = request.json.get('afterq')
        answer = request.json.get('aftera')
        card = Card.query.filter_by(id=id, email=email).first()
        if not card:
            return jsonify({'msg': 'no'}), 200
        card.question = question
        card.answer = answer
        db.session.commit()
        return jsonify({'msg': 'ok'}), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
@app.route('/learn/getone', methods=['POST'])
def get_one_card():
    if current_user.is_authenticated:
        email = current_user.email
        id = request.json.get('card')
        card = Card.query.filter_by(id=id, email=email).first()
        card=card[0]
        if not card[0]:
            return jsonify({'msg': 'no'}), 200
        return jsonify({
            'question': card.question,
            'answer': card.answer,
            'id': card.id
        }), 200
    else:
        return jsonify({'msg': 'no'}), 200
    
    
        
       
if __name__ == '__main__':
    app.run(debug=True)
    
