# CloudSkill 安裝指南

CloudSkill 的 `.agents/skills/` 是 Codex 與 Claude Code 的 canonical Skill 來源。建議先將 Repository Clone 到固定本機路徑，再由各工作專案從該路徑安裝、更新並寫入私人 Eval Inbox。

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

## 2. 安裝模式

- **User scope**：同一位使用者的多個專案共用 Skills 與 `~/.cloudskill/config.json`。
- **Project scope**：只對指定專案生效，並寫入不應提交的 `<project>/.cloudskill/config.local.json`。
- **Skills-only**：使用 `-SkipGuidance` / `--skip-guidance`，不匯入個人架構 Guidance。
- **No local config**：使用 `-SkipLocalConfig` / `--skip-local-config`；此模式無法使用簡短的正向／負向案例收集流程。

## 3. Windows PowerShell

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

## 4. macOS / Linux / WSL / Git Bash

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

## 5. 安裝結果

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

## 6. 本機設定與 Eval Inbox

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
- 強制 sanitization 與禁止 raw transcript、auto skill modification、auto commit、auto push 的安全值

Inbox 結構：

```text
.local/eval-inbox/
├── candidates/
├── manual-review/
├── processed/
├── rejected/
└── sensitive-terms.local.txt
```

`.local/` 與 `config.local.json` 均由 Git 忽略。請將公司、客戶、專案、產品、設備、人員與其他私人識別字加入 `sensitive-terms.local.txt`；不要將該檔案提交。

## 7. 日常正向與負向案例

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
3. 產生候選 JSON，並呼叫本機 CloudSkill Repository 的 `scripts/capture_eval_candidate.py`。
4. 安全案例寫入 `candidates/`；有疑慮的案例寫入 `manual-review/`。
5. 不修改正式 `evals/`、技能、Commit、Tag、Branch 或 Remote。

缺少有效設定時，Agent 應停止並要求重新執行安裝，不得自行猜測寫入位置。

## 8. 批次整理到 CloudSkill

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

## 9. 更新

```bash
cd /path/to/CloudSkill
git pull
```

回到工作專案後重新執行原安裝命令。安裝器會更新 Skills、Guidance 受管理區塊、本機版本與路徑設定，但不刪除 Inbox 內容或非 CloudSkill 技能。

## 10. 驗證

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

## 11. 官方參考

- OpenAI Codex Skills: https://developers.openai.com/codex/build-skills
- OpenAI Codex AGENTS.md: https://developers.openai.com/codex/agent-configuration/agents-md
- Anthropic Claude Code Skills: https://code.claude.com/docs/zh-TW/skills
- Anthropic Claude Code Memory/CLAUDE.md: https://docs.anthropic.com/zh-CN/docs/claude-code/memory
