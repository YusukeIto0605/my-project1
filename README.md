# 書籍管理システム

## 概要
Flask（Python）とMySQLを使った書籍管理Webアプリです。  
書籍の登録、編集、削除、画像アップロード、検索、並び替え、ページネーション機能を備えています。

## 動作環境
- Python 3.8以上
- Flask
- Flask-SQLAlchemy
- PyMySQL
- MySQL 5.7以上（ポート3307設定）
- Webブラウザ（HTML5対応）

## インストールとセットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/ユーザー名/リポジトリ名.git
cd リポジトリ名

依存パッケージをインストール
pip install -r requirements.txt

MySQLの準備
データベース名：books
ユーザー名：books
パスワード：books
ポート番号：3307
必要に応じてapp.pyのSQLALCHEMY_DATABASE_URIを書き換えてください。

テーブルの作成（初回のみ）
from app import db
db.create_all()

アプリを起動
python app.py

ブラウザでアクセス
http://localhost:5000

主な機能

書籍一覧の表示・検索・並び替え
書籍の新規登録（複数画像アップロード対応）
書籍情報の編集・削除
ページネーション機能
画像表示

ディレクトリ構成例
/static/uploads/   # 画像保存ディレクトリ
/templates/        # HTMLテンプレート（wp.html, edit.htmlなど）
app.py            # Flaskアプリ本体
requirements.txt   # 依存パッケージリスト
README.md          # この説明ファイル

注意事項

画像アップロードはPNG, JPG, JPEG, GIFのみ対応
本番環境ではapp.secret_keyやDBパスワードを環境変数等で安全に管理してください
UNIXソケット接続とTCP接続の違いに注意（hostとportの設定）
secure_filename()でファイル名の安全性を確保しています
