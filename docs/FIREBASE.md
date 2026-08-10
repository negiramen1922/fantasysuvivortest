# Firebase 連携（Google認証・クラウドセーブ・解析）セットアップ

勇者サバイバーに **Googleログイン**・**別端末でのセーブ持ち越し**・**アクセス数/武器使用率などの解析** を追加するための手順。
実装はすべて「未設定なら何もしない（ゲームはローカルのみで通常動作）」ように作ってあるので、下記を設定した時点で有効化されます。

---

## 1. Firebase プロジェクトを作る
1. https://console.firebase.google.com/ →「プロジェクトを追加」。
2. Google アナリティクスは **有効** のまま作成（アクセス数・イベント集計に使います）。

## 2. Web アプリを登録して構成を取得
1. プロジェクト概要 → 「</>（ウェブ）」でアプリを追加。
2. 表示される `firebaseConfig`（apiKey / authDomain / projectId / appId / measurementId など）をコピー。
3. リポジトリ直下の **`firebase-config.js`** の `window.FIREBASE_CONFIG` に貼り付けてコミット。
   - この値は公開されても問題ありません（クライアント識別子）。安全性は下記の Firestore ルールと承認済みドメインで担保します。

## 3. Google ログインを有効化
- Authentication → 「始める」→ Sign-in method → **Google** を有効化。
- Authentication → Settings → **承認済みドメイン** に本番ドメインを追加：
  - `negiramen1922.github.io`
  - （ローカル確認する場合）`localhost`

## 4. Firestore（クラウドセーブ）
1. Firestore Database → データベースを作成（本番モードでOK）。
2. ルールを以下にする（各ユーザーは自分のセーブだけ読み書き可）：

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /saves/{uid} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

- セーブは `saves/{uid}` に `{ save: <localStorageのbsv_save文字列>, prog: 進行度スコア, ts: 更新時刻 }` で保存されます。

## 5. 解析（Analytics / GA4）
- 上で Analytics を有効にしていれば自動で **アクセス数・セッション** が記録されます。
- 追加のカスタムイベント：
  - `game_open` … 起動時（バージョン付き）
  - `run_end` … ラン終了時（`stage / won / time_sec / level / score / kills / weapon_count / weapons`）
  - `weapon_used` … そのランで使った武器ごとに1件（`weapon / name / stage`）
- **武器の使用率** ＝ 各 `weapon` の `weapon_used` 件数 ÷ `run_end` 件数。
  - GA4 では「イベント」→ `weapon_used` を開き、パラメータ `weapon` での内訳を確認（カスタムディメンジョン登録推奨）。
  - より詳細に集計したい場合は GA4 の **BigQuery エクスポート** を有効化すると SQL で集計できます。

## 挙動メモ
- ログイン時、ローカルとクラウドで進行度が違う場合は **選択ダイアログ** が出ます（選んだ方を両端末へ反映）。
- セーブのたびにデバウンス（約1.5秒）でクラウドへ自動アップロード。
- Firebase SDK は Google CDN（gstatic）から読み込みます。読み込めない/未設定の環境では自動的に無効化され、ゲームはローカルセーブのみで動きます。
