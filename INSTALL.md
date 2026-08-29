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

安裝器不保存 GitHub Token 或其他憑證。


## 2. Plugin 模式（建議）

完整說明見 [docs/CLOUDBOX_PLUGIN.md](docs/CLOUDBOX_PLUGIN.md)。Plugin 安裝本身不會建立本機 config；若是 coding agent 代為安裝，裝完後應主動詢問是否要另外補上本機 config，見第 3 節「由 coding agent 代為安裝時」。

### Codex／ChatGPT

```powershell
codex plugin marketplace add D:\Git\CloudSkill
codex plugin add cloudbox-skills@cloudbox-marketplace
codex plugin list
```

重新整理 Plugins Directory，在 **CloudBox** marketplace 安裝 **CloudBox**。OpenAI manifest 會使用 CloudBox 圖示、Logo 與品牌色。


### Claude Code

```powershell
claude plugin marketplace add D:\Git\CloudSkill
claude plugin install cloudbox-skills@cloudbox-marketplace --scope user
claude plugin list
```

安裝後執行 `/reload-plugins`。Claude Code 的明確技能名稱為 `/cloudbox-skills:<skill-name>`。

Plugin 模式可與 Superpowers 等其他 Plugin 同時安裝，但應在 Host 中停用不需要的 Plugin，或明確劃分 generic development workflow 與 CloudBox domain/architecture responsibility。CloudBox 不會自行修改其他 Plugin 的啟用狀態。


## 3. Standalone 安裝模式

- **User scope**：同一位使用者的多個專案共用 Skills 與 `~/.cloudbox-skills/config.json`。
- **Project scope**：只對指定專案生效，並寫入不應提交的 `<project>/.cloudbox-skills/config.local.json`。
- **Skills-only**：使用 `-SkipGuidance` / `--skip-guidance`，不匯入個人架構 Guidance。

## 4. Windows PowerShell

### 從固定本機 CloudSkill 安裝到目前 Project

```powershell
& "D:\Git\CloudSkill\scripts\install.ps1" `
  -Tool both `
  -Scope project `
  -ProjectPath (Get-Location).Path `
  -CloudSkillRepoPath "D:\Git\CloudSkill"
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


## 10. 更新

```bash
cd /path/to/CloudSkill
git pull
```

回到工作專案後重新執行原安裝命令。安裝器會更新 Skills、Guidance 受管理區塊、本機版本與路徑設定，但不刪除 Inbox 內容或非 CloudSkill 技能。

## 10b. Claude Desktop／claude.ai 網頁版

跟前面的 CLI 安裝不同：claude.ai 網頁版與 Claude Desktop 是「Customize/Settings → Skills → 上傳 zip」，一次一個技能，而且**不會跟 Claude Code CLI 同步**——三個介面要分別上傳管理。zip 結構有硬性規定：技能資料夾本身必須在 zip 根目錄（`<skill-name>/SKILL.md`），不能多包一層。

打包（只會包含 `config/skill-portability.json` 裡標記 `portable`／`hybrid` 的技能）：

```bash
python3 scripts/package_surface_skills.py
# 輸出到 .local/surface-packages/<skill-name>.zip
```

完整支援矩陣、各技能的可攜性分類、目前已知限制，見 [docs/PLATFORM_SUPPORT_MATRIX.md](docs/PLATFORM_SUPPORT_MATRIX.md)。**這個打包腳本只驗證過 zip 結構正確，還沒有人實際上傳到 claude.ai 帳號驗證過會不會動。**

## 10c. Gemini CLI

CloudBox 的 Gemini extension 由 canonical `.agents/skills/` 產生，不直接修改：

```bash
python3 scripts/sync_gemini_plugins.py --check
gemini extensions install /path/to/cloudbox-skills/gemini-plugin
```


目前已驗證 manifest、tier、檔案內容與隔離複製；此工作站尚未安裝
Gemini CLI，所以真實 install 與 `/skills list` 仍為 `NOT RUN`。


## 11. 驗證

```bash
python scripts/run_all_checks.py
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
