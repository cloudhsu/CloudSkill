# CloudBox／CloudSkill 安裝指南

CloudBox 是外掛顯示品牌，`CloudSkill` 是 Repository 與既有內部相容名稱。`.agents/skills/` 是 Codex、ChatGPT 與 Claude Code 共用的 canonical Skill 來源。可選擇 Plugin 模式或既有 Standalone 模式；同一個 Host 不要同時載入兩份 CloudBox 技能。

## 1. Clone 到固定本機路徑

Windows：

```powershell
git clone https://github.com/cloudhsu/CloudSkill.git D:\Git\CloudSkill
```

macOS / Linux：

```bash
git clone https://github.com/cloudhsu/CloudSkill.git ~/Git/CloudSkill
```

安裝器不保存 GitHub Token 或其他憑證，只保存本機 Repository 與 Eval Inbox 絕對路徑。


## 2. Plugin 模式（建議）

完整說明見 [docs/CLOUDBOX_PLUGIN.md](docs/CLOUDBOX_PLUGIN.md)。

### Codex／ChatGPT

```powershell
codex plugin marketplace add D:\Git\CloudSkill
```

重新整理 Plugins Directory，在 **CloudBox** marketplace 安裝 **CloudBox**。OpenAI manifest 會使用 CloudBox 圖示、Logo 與品牌色。

### Claude Code

```powershell
claude plugin marketplace add D:\Git\CloudSkill
claude plugin install cloudbox@cloudbox-marketplace --scope user
claude plugin list
```

安裝後執行 `/reload-plugins`。Claude Code 的明確技能名稱為 `/cloudbox:<skill-name>`。

Plugin 模式可與 Superpowers 等其他 Plugin 同時安裝，但應在 Host 中停用不需要的 Plugin，或明確劃分 generic development workflow 與 CloudBox domain/architecture responsibility。CloudBox 不會自行修改其他 Plugin 的啟用狀態。

Plugin 模式若要使用 `整理成正向案例`／`整理成負向案例`，只建立本機設定與 Eval Inbox，不複製第二份技能：

```powershell
& "D:\Git\CloudSkill\scripts\install.ps1" `
  -Scope user `
  -CloudSkillRepoPath "D:\Git\CloudSkill" `
  -ConfigOnly
```

## 3. Standalone 安裝模式

- **User scope**：同一位使用者的多個專案共用 Skills 與 `~/.cloudskill/config.json`。
- **Project scope**：只對指定專案生效，並寫入不應提交的 `<project>/.cloudskill/config.local.json`。
- **Skills-only**：使用 `-SkipGuidance` / `--skip-guidance`，不匯入個人架構 Guidance。
- **No local config**：使用 `-SkipLocalConfig` / `--skip-local-config`；此模式無法使用簡短的正向／負向案例收集流程。

## 4. Windows PowerShell

### 從固定本機 CloudSkill 安裝到目前 Project

```powershell
& "D:\Git\CloudSkill\scripts\install.ps1" `
  -Tool both `
  -Scope project `
  -ProjectPath (Get-Location).Path `
  -CloudSkillRepoPath "D:\Git\CloudSkill"
```

未指定 `-EvalInboxPath` 時，預設使用：

```text
D:\Git\CloudSkill\.local\eval-inbox
```

指定獨立私人 Inbox：

```powershell
& "D:\Git\CloudSkill\scripts\install.ps1" `
  -Tool codex `
  -Scope project `
  -ProjectPath "D:\Work\EquipmentProject" `
  -CloudSkillRepoPath "D:\Git\CloudSkill" `
  -EvalInboxPath "D:\Private\CloudSkill-Eval-Inbox"
```

User scope：

```powershell
& "D:\Git\CloudSkill\scripts\install.ps1" `
  -Tool both `
  -Scope user `
  -CloudSkillRepoPath "D:\Git\CloudSkill"
```

## 5. macOS / Linux / WSL / Git Bash

```bash
chmod +x ~/Git/CloudSkill/scripts/install.sh
~/Git/CloudSkill/scripts/install.sh \
  --tool both \
  --scope project \
  --project-path "$PWD" \
  --cloudskill-repo-path ~/Git/CloudSkill
```

指定私人 Inbox：

```bash
~/Git/CloudSkill/scripts/install.sh \
  --tool codex \
  --scope project \
  --project-path ~/Work/EquipmentProject \
  --cloudskill-repo-path ~/Git/CloudSkill \
  --eval-inbox-path ~/Private/CloudSkill-Eval-Inbox
```

## 6. 安裝結果

### Codex

```text
User:    ~/.agents/skills/<skill-name>/SKILL.md
Project: <repo>/.agents/skills/<skill-name>/SKILL.md
```

### Claude Code

```text
User:    ~/.claude/skills/<skill-name>/SKILL.md
Project: <repo>/.claude/skills/<skill-name>/SKILL.md
```

完整安裝時，Codex 使用受管理的 `AGENTS.md` 區塊；Claude Code 透過 `CLAUDE.md` 匯入同一份 Guidance。安裝器只替換 CloudSkill 同名技能，並保留受管理區塊外的既有內容。

## 7. 本機設定與 Eval Inbox

Project scope 設定：

```text
<project>/.cloudskill/config.local.json
```

User scope 設定：

```text
~/.cloudskill/config.json
```

設定包含：

- `cloudskill_repository`
- `eval_inbox`
- `sensitive_terms_path`
- `eval_exchange_repo`（選填，見第 8d 節）
- 強制 sanitization 與禁止 raw transcript、auto skill modification、auto commit、auto push 的安全值

Inbox 結構：

```text
.local/eval-inbox/
├── candidates/
├── manual-review/
├── processed/
├── rejected/
├── synced/              # 已透過 sync_eval_exchange.py --push 送出的候選（保留，不會刪除，見第 8d 節）
├── imports/            # 從外部/中斷連線 session 匯出的壓縮檔，放在這裡等待匯入（見第 8b、8d 節）
│   └── processed/       # 已匯入的壓縮檔（保留供追溯，不會刪除）
└── sensitive-terms.local.txt
```

`.local/` 與 `config.local.json` 均由 Git 忽略。請將公司、客戶、專案、產品、設備、人員與其他私人識別字加入 `sensitive-terms.local.txt`；不要將該檔案提交。

## 8. 日常正向與負向案例

在已設定的專案內，直接對 Codex 或 Claude Code 說：

```text
整理成正向案例
```

或：

```text
整理成負向案例
```

Agent 應使用 `developing-skills`：

1. 只擷取理解案例所需的相關互動。
2. 預設去除識別資訊，不保存完整對話。
3. 產生候選 JSON。若 `.cloudskill/config.local.json` 或 `~/.cloudskill/config.json` 能解析到本機可存取的 CloudSkill Repository，呼叫其 `scripts/capture_eval_candidate.py`，直接寫入 Eval Inbox。
4. 安全案例寫入 `candidates/`；有疑慮的案例寫入 `manual-review/`。
5. 不修改正式 `evals/`、技能、Commit、Tag、Branch 或 Remote。

缺少有效設定、且本機也無法存取任何 CloudSkill Repository 時（例如外部/中斷連線的 session），Agent 不得自行猜測寫入位置，應改用第 8b 節的匯出流程，而不是放棄擷取。

## 8b. 外部／中斷連線 session：匯出後帶回 CloudSkill

當 Agent 只有已安裝的技能、卻沒有本機 CloudSkill Repository 可寫入時，使用這組技能自帶的匯出工具：

```bash
python3 .claude/skills/developing-skills/assets/export_eval_candidate.py \
  --kind positive --input draft.json
```

行為：

- 驗證規則與 `capture_eval_candidate.py` 相同，但不需要任何設定檔（純標準函式庫，跟著技能一起安裝）。
- 寫入目前專案內、免設定的 `.cloudskill/eval-outbox/{candidates,manual-review}/`。
- 打包成 `CloudSkill-eval-export-<label>-<timestamp>.zip`，印出確切路徑。
- 因為通常沒有可用的私人 `sensitive-terms.local.txt`，預設保守地將案例歸類為 `manual-review`（若這台機器剛好有私人詞彙檔，可用 `--sensitive-terms PATH` 傳入）。

接著把印出的壓縮檔手動搬到（USB、雲端硬碟、內部傳檔皆可）：

```text
<CloudSkillRepo>/.local/eval-inbox/imports/
```

在 CloudSkill Repository 內執行匯入：

```bash
python3 scripts/import_eval_candidates.py
```

匯入時會：重新驗證每筆候選、用 Repository 自己的 `sensitive-terms.local.txt` 再掃描一次、比對已存在的候選去除重複、分別歸類到 `candidates/`、`manual-review/`、或 `rejected/`，並把已處理的壓縮檔移到 `imports/processed/`（不會刪除原始檔）。這一步同樣不修改正式 `evals/`、技能、Commit 或 Remote。

## 8c. 分析專案歷史匯出優化案例

適用情境：想從一個已裝好 CloudBox 的專案（你自己的專案，或抓下來的開源專案）挖出可遷移的工程原則，而不是從一次即時互動擷取。

在已設定的專案內，對 Codex 或 Claude Code 說：

```text
從專案提煉優化案例
```

Agent 應使用 `developing-skills`（見 `references/conversation-derived-optimization.md` 的「Project-history mining」）：

1. 不逐筆讀完整個 commit history。先看 tag/release、`CHANGELOG.md`、架構文件，再依訊號（重構/修復/重設計字眼、大 diff、被 CHANGELOG 或 ADR 提到）挑出有意義的節點，詳細讀取數量有上限，並明講排除了什麼。你可以隨時明確指定時間範圍、tag 區間或子目錄，蓋掉自動界定。
2. 每筆候選的信心度標記只能是 `inferred` 或 `unknown`，不可以是 `observed`——commit history 看不出真正的推理過程。
3. 分析別人的開源專案時，只萃取「可遷移的工程壓力」，不複製原始碼或商業邏輯；日後若真的變成正式技能參考，需明確標註來源專案（見 `skill-authoring-sources.md`）。
4. 輸出走跟第 8/8b 節一樣的管線：本機可連到 CloudSkill Repository 就用 `capture_eval_candidate.py`，連不到就用 `export_eval_candidate.py` 打包 zip；額外產生一份 `EVAL_MINING_REPORT.md` 摘要一起放進 zip。
5. 不修改正式 `evals/`、技能、Commit、Tag、Branch 或 Remote——這仍然只是證據暫存，正式收斂一樣要走第 9 節的批次審查。

## 8d. 用 Git 在多台機器間傳遞候選案例

情境：第二台機器（例如公司筆電）也裝了 Codex/Claude 且也能連到 CloudSkill Repository，但候選案例還是出不來——因為 `.local/eval-inbox/` 在**每一台機器上**都被 Git 忽略，不會因為兩邊都連得到同一個 Repository 就自動同步。這不是第 8b 節那種「連不到 Repository」的情境，是「兩邊都連得到，但私人候選資料本來就不該進 Git history」的情境。

在 `.cloudskill/config.local.json` / `~/.cloudskill/config.json` 裡加一個你自己擁有的私有 Git repository（純粹當傳輸層，不是 CloudSkill 本身）：

```json
{
  "eval_exchange_repo": "git@github.com:<you>/cloudskill-eval-exchange.git"
}
```

在**擷取候選的那台機器**：

```bash
python3 scripts/sync_eval_exchange.py --push
```

會把 `candidates/`／`manual-review/` 裡還沒送出的候選打包、commit、push 到 exchange repository 的 `incoming/`，來源檔案本機移到 `synced/`（保留，不刪除）。

在**你實際審查、host CloudSkill Repository 的那台機器**：

```bash
python3 scripts/sync_eval_exchange.py --pull
python3 scripts/import_eval_candidates.py
```

`--pull` 會把 exchange repository 裡還沒處理過的壓縮檔複製進 `eval_inbox/imports/`，之後跟第 8b 節的匯入流程完全一樣（重新驗證、用本機私人詞彙表重新掃描、去重）。兩個方向都是冪等的——沒有新東西時重跑不會出錯，也不會重複處理。

## 9. 批次整理到 CloudSkill

累積候選案例後，在 CloudSkill Repository 啟動 Agent：

```powershell
cd D:\Git\CloudSkill
codex
```

使用：

```text
使用 developing-skills 整理 Eval Inbox，重新掃描識別資訊、合併重複案例、判斷 Skill Owner，建立正式 Eval 分支並執行完整檢查；不要自動 Push。
```

正式 `evals/` 只接受已審查、可公開、可重播的案例。候選案例不是行為測試 PASS，也不應直接原封不動提交。

## 10. 更新

```bash
cd /path/to/CloudSkill
git pull
```

回到工作專案後重新執行原安裝命令。安裝器會更新 Skills、Guidance 受管理區塊、本機版本與路徑設定，但不刪除 Inbox 內容或非 CloudSkill 技能。

## 10b. Claude Desktop／claude.ai 網頁版

跟前面的 CLI 安裝不同：claude.ai 網頁版與 Claude Desktop 是「Customize/Settings → Skills → 上傳 zip」，一次一個技能，而且**不會跟 Claude Code CLI 同步**——三個介面要分別上傳管理。zip 結構有硬性規定：技能資料夾本身必須在 zip 根目錄（`<skill-name>/SKILL.md`），不能多包一層。

打包（只會包含 `config/skill-portability.json` 裡標記 `portable`／`hybrid` 的技能；`local-runtime-eval-debugging` 這種依賴本機 Repository 的技能會被排除，因為在沙盒環境裡本來就跑不動）：

```bash
python3 scripts/package_surface_skills.py
# 輸出到 .local/surface-packages/<skill-name>.zip
```

完整支援矩陣、各技能的可攜性分類、目前已知限制，見 [docs/PLATFORM_SUPPORT_MATRIX.md](docs/PLATFORM_SUPPORT_MATRIX.md)。**這個打包腳本只驗證過 zip 結構正確，還沒有人實際上傳到 claude.ai 帳號驗證過會不會動。**

## 10c. Gemini CLI

Gemini CLI 官方文件宣稱原生支援 `.agents/skills/` 這個路徑別名，理論上不用額外打包就能讀到 CloudSkill 的技能——但這只是查證官方文件得到的結論，**還沒有人實際裝一次 Gemini CLI 驗證過**。狀態記錄在 [docs/PLATFORM_SUPPORT_MATRIX.md](docs/PLATFORM_SUPPORT_MATRIX.md)。

## 11. 驗證

```bash
python scripts/run_all_checks.py
```

Codex：

```text
/skills
$developing-skills
```

Claude Code：

```text
/skills
/memory
/developing-skills
```

## 12. 官方參考

- OpenAI Codex Plugins: https://developers.openai.com/codex/build-plugins
- OpenAI Plugin Packaging: https://developers.openai.com/plugins/build/plugins
- OpenAI Codex Skills: https://developers.openai.com/codex/build-skills
- OpenAI Codex AGENTS.md: https://developers.openai.com/codex/agent-configuration/agents-md
- Anthropic Claude Code Plugins: https://code.claude.com/docs/zh-TW/plugins
- Anthropic Claude Code Plugin Marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Anthropic Claude Code Skills: https://code.claude.com/docs/zh-TW/skills
- Anthropic Claude Code Memory/CLAUDE.md: https://docs.anthropic.com/zh-CN/docs/claude-code/memory
