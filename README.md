# PAC IP Manager

PAC ファイルで利用する SaaS / クラウドサービスの公式 IP リスト・URL リストを毎日取得し、共通 JSON フォーマットへ正規化して保存するための GitHub Actions ワークフローです。

## 対象サービス

| Service | Source | Output |
| --- | --- | --- |
| Microsoft 365 | `https://endpoints.office.com/endpoints/worldwide?...` | `urls` -> `url`, `ips` -> `ip_range` |
| Microsoft Teams | `https://endpoints.office.com/endpoints/worldwide?...` | Microsoft Teams records only: `urls` -> `url`, `ips` -> `ip_range` |
| Zoom | `https://assets.zoom.us/docs/ipranges/Zoom.txt` | 各行 -> `ip_range` |
| Zoom Cloud Meetings | `https://assets.zoom.us/docs/ipranges/Zoom.txt` | 各行 -> `ip_range` |
| Cisco Webex Meetings | `https://help.webex.com/en-us/article/WBX264/Network-Requirements-for-Webex-Services` | CIDR -> `ip_range`, domains -> `url` / `fqdn` |
| Windows Update | `https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints` | Windows Update section destinations -> `url` / `fqdn` |
| Apple | `https://support.apple.com/en-us/101555` | ホスト名 -> `fqdn` / ワイルドカード -> `url` |
| Google Workspace | `https://www.gstatic.com/ipranges/goog.json` | `prefixes[].ipv4Prefix` -> `ip_range` |
| Google Meet | `https://support.google.com/a/answer/1279090?hl=en-GB` | Meet URIs/SNI -> `fqdn` / `url`, media CIDR -> `ip_range` |
| Box | Box firewall support page and `https://support.box.com/ips` | domains -> `url` / `fqdn`, CIDR -> `ip_range` |

## JSON フォーマット

```json
{
  "service": "microsoft365",
  "updated_at": "2026-06-06",
  "schema_version": "1",
  "entries": [
    {
      "type": "url",
      "value": "*.office365.com",
      "action": "DIRECT"
    },
    {
      "type": "ip_range",
      "value": "13.107.6.152/31",
      "action": "DIRECT"
    }
  ]
}
```

`type` は `url`, `ip_range`, `fqdn` のいずれかです。`action` は現時点では `DIRECT` 固定です。

## ローカル実行

```bash
python -m pip install -r requirements.txt
python main.py
```

特定サービスのみ実行する場合:

```bash
python main.py --service zoom
python main.py --service microsoft_teams
python -m fetchers.microsoft365
```

実行結果は `ip-lists/latest/{service}.json` と `ip-lists/history/{service}/{service}-YYYY-MM-DD.json` に保存されます。既存の latest と比較して内容に差分がない場合は保存をスキップします。差分判定では `updated_at` のみの変化は無視します。

ログはデフォルトで `logs/fetch-YYYY-MM-DD.log` に保存されます。保存先を変更する場合:

```bash
PAC_IP_MANAGER_LOG_DIR=/tmp/pac-ip-manager-logs python main.py
```

## テスト

```bash
python -m pytest
```

テストでは実際の HTTP 通信は行わず、各 fetcher の `normalize` と JSON Schema バリデーションを確認します。

## GitHub Actions

`.github/workflows/fetch-daily.yml` は毎日 21:00 JST に実行されます。手動実行も `workflow_dispatch` から可能です。

ワークフローの流れ:

1. リポジトリを checkout
2. Python 3.11 をセットアップ
3. 依存関係をインストール
4. テストを実行
5. `main.py` を実行
6. daily log を artifact として保存
7. `ip-lists` に差分があれば `github-actions[bot]` で commit / push
8. latest JSON を Cloudflare KV に PUT

Cloudflare KV 連携には以下の GitHub Secrets が必要です。

| Secret | Purpose |
| --- | --- |
| `CF_ACCOUNT_ID` | Cloudflare Account ID |
| `CF_API_TOKEN` | Cloudflare API Token |
| `CF_KV_NAMESPACE_ID` | KV Namespace ID |

KV のキー名はサービス名です。例: `microsoft365`, `microsoft_teams`, `zoom`, `zoom_cloud_meetings`, `webex_meetings`, `windows_update`, `apple`, `google`, `google_meet`, `box`

## 依存関係の自動更新

`.github/dependabot.yml` で Dependabot を有効化しています。GitHub Actions と pip 依存関係の更新 PR が週次で作成されます。

## 履歴削除

90 日以前の履歴削除ワークフローは現時点では未実装です。
