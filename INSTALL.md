# CloudSkill 安裝指南

CloudSkill 的 `SKILL.md` 採用共同的 Agent Skills 結構，因此同一份 Skill 可以供 Codex 與 Claude Code 使用；差異主要是安裝目錄與叫用語法。

## 1. 先決條件

Clone Repository：

```bash
git clone https://github.com/cloudhsu/CloudSkill.git
cd CloudSkill
```

CloudSkill 的唯一 Skill 原始來源是：

```text
.agents/skills/
```

不要同時手動維護 `.agents/skills` 與 `.claude/skills` 兩份內容。Claude Code 的目錄由安裝 Script 從 canonical source 複製。

## 2. 建議安裝模式

### 個人完整模式

適合 Repository 擁有者：安裝全部 Skills，並加入個人的架構工作原則。

### Skills-only 模式

適合其他使用者或團隊：只安裝 Skills，不匯入 `AGENTS.md` 中的個人架構背景。

### Project 模式

只對指定 Repository 生效，適合團隊共同 Commit。

## 3. Windows PowerShell

### Codex 與 Claude Code，個人完整安裝

```powershell
.\scripts\install.ps1 -Tool both -Scope user
```

### 只安裝 Skills

```powershell
.\scripts\install.ps1 -Tool both -Scope user -SkipGuidance
```

### 安裝到指定 Project

```powershell
.\scripts\install.ps1 `
  -Tool both `
  -Scope project `
  -ProjectPath "D:\Work\MyProject"
```

### 只安裝 Codex 或 Claude Code

```powershell
.\scripts\install.ps1 -Tool codex -Scope user
.\scripts\install.ps1 -Tool claude -Scope user
```

## 4. macOS / Linux / WSL / Git Bash

```bash
chmod +x scripts/install.sh
```

### Codex 與 Claude Code，個人完整安裝

```bash
./scripts/install.sh --tool both --scope user
```

### 只安裝 Skills

```bash
./scripts/install.sh --tool both --scope user --skip-guidance
```

### 安裝到指定 Project

```bash
./scripts/install.sh \
  --tool both \
  --scope project \
  --project-path /path/to/project
```

## 5. Codex 安裝結果

### 個人範圍

```text
~/.agents/skills/<skill-name>/SKILL.md
~/.codex/AGENTS.md
```

### Project 範圍

```text
<repo>/.agents/skills/<skill-name>/SKILL.md
<repo>/AGENTS.md
```

Codex 會從目前目錄向 Repository root 搜尋 `.agents/skills`；個人 Skills 位於 `$HOME/.agents/skills`。全域指令預設位於 `~/.codex/AGENTS.md`。

驗證：

```text
/skills
$architecture-review
```

也可以執行：

```bash
codex --ask-for-approval never "Summarize the current instructions and list the CloudSkill skills you can see."
```

## 6. Claude Code 安裝結果

### 個人範圍

```text
~/.claude/skills/<skill-name>/SKILL.md
~/.claude/cloudskill/AGENTS.md
~/.claude/CLAUDE.md
```

安裝器會在 `~/.claude/CLAUDE.md` 加入受管理的 import：

```text
@~/.claude/cloudskill/AGENTS.md
```

### Project 範圍

```text
<repo>/.claude/skills/<skill-name>/SKILL.md
<repo>/AGENTS.md
<repo>/CLAUDE.md
```

Project 的 `CLAUDE.md` 使用：

```text
@AGENTS.md
```

這使 Codex 與 Claude Code 共用同一份專案規範，而不複製內容。

Claude Code 叫用方式：

```text
/architecture-review
/application-client-server-architecture
```

可使用 `/skills` 檢查 Skill，使用 `/memory` 檢查載入的 `CLAUDE.md`。

## 7. 更新

```bash
git pull
```

重新執行相同安裝命令。安裝器會：

- 只替換 CloudSkill 同名 Skill 目錄。
- 不刪除其他來源的 Skills。
- 更新受 `CLOUDSKILL:BEGIN/END` 標記管理的 Guidance 區段。
- 保留標記以外的既有 `AGENTS.md`／`CLAUDE.md` 內容。

## 8. 手動安裝

### Codex

```bash
mkdir -p ~/.agents/skills ~/.codex
cp -R .agents/skills/* ~/.agents/skills/
cp AGENTS.md ~/.codex/AGENTS.md
```

### Claude Code

```bash
mkdir -p ~/.claude/skills ~/.claude/cloudskill
cp -R .agents/skills/* ~/.claude/skills/
cp AGENTS.md ~/.claude/cloudskill/AGENTS.md
printf '\n@~/.claude/cloudskill/AGENTS.md\n' >> ~/.claude/CLAUDE.md
```

手動指令可能覆蓋或重複既有設定；已有自訂內容時，優先使用安裝 Script。

## 9. 相容性說明

- `SKILL.md` 的 `name`、`description`、references、assets 與 scripts 可由兩個工具共用。
- `agents/openai.yaml` 是 Codex/OpenAI 的額外 metadata；Claude Code 會忽略它，不需刪除。
- Claude Code 支援額外 frontmatter，但 CloudSkill 不依賴 Claude 專屬欄位，因此 canonical Skill 保持可攜。
- Codex 以 `$skill-name` 明確叫用；Claude Code 以 `/skill-name` 明確叫用。

## 10. 官方參考

- OpenAI Codex Skills: https://developers.openai.com/codex/build-skills
- OpenAI Codex AGENTS.md: https://developers.openai.com/codex/agent-configuration/agents-md
- Anthropic Claude Code Skills: https://code.claude.com/docs/zh-TW/skills
- Anthropic Claude Code Memory/CLAUDE.md: https://docs.anthropic.com/zh-CN/docs/claude-code/memory
