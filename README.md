## 環境構築

1. 仮想環境の作成
   ```bash
   python -m venv venv
   ```

2. 仮想環境の有効化
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. 必要なパッケージのインストール
   ```bash
   pip install -r requirements.txt
   ```

---

## アプリケーション概要

このFlaskアプリケーションは、学習支援用のカード管理・タイマー・フォルダ管理・ユーザー認証機能を提供します。  
データベースにはSQLiteを使用し、SQLAlchemyでORM管理しています。CORSやセッション管理、パスワードのハッシュ化、ログイン状態の管理も実装されています。

---

### データベース構成

- **User**  
  ユーザー情報（id, username, email, password）

- **Folder**  
  フォルダ情報（id, email, folder名, 作成日時）

- **Card**  
  学習カード（id, email, folder名, question, answer, ydata, date, 作成日時）

- **Time**  
  タイマー記録（id, email, date, time, 作成日時）

---

### 主なAPIエンドポイント

#### 認証関連

- `POST /account/signup`  
  新規ユーザー登録（name, mail, pas）

- `POST /account/login`  
  ログイン（mail, pas）

- `GET /account/loginnow`  
  ログイン状態確認

- `GET /account/logout`  
  ログアウト（要ログイン）

---

#### タイマー関連

- `POST /timer`  
  タイマー記録の追加（date, time）

- `GET /timer`  
  タイマー記録の取得

---

#### フォルダ・カード関連

- `POST /learn/folder`  
  フォルダ作成（folder名）

- `GET /learn/getfolder`  
  フォルダ一覧取得

- `POST /learn/makecard`  
  カード作成（fid, question, answer）

- `POST /learn/getall`  
  指定フォルダ内の全カード取得（id: フォルダID）

- `POST /learn/get`  
  指定フォルダ内のカードを最大10件取得(忘却曲線を基準にして前回前回不正解だったものが選ばれやすいようにしている)（id: フォルダID、バブルソートで優先度順）

- `POST /learn/in`  
  カードのydata, date更新（card_id, ydata）

- `POST /learn/delete`  
  カード削除（card_id）

- `POST /learn/editcard`  
  カード編集（card_id, afterq, aftera）

- `POST /learn/getone`  
  1件のカード取得（card: カードID）

---

### ログイン・セッション管理

- Flask-Loginでユーザー認証・セッション管理
- パスワードはハッシュ化して保存
- セッションはCookieベースで管理（ローカル開発用設定）

---

### 注意事項

- すべてのカード・フォルダ・タイマー操作APIはログイン状態が必要です。
- レスポンスはJSON形式です。

---

詳細な実装は `study_support_backend/main.py` を参照してください。