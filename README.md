# Software Architect Codex Pack

這是一套給 Codex 使用的個人架構工作規則與 Skills。

## 內容

```text
software-architect-codex-pack/
├── AGENTS.md
└── .agents/
    └── skills/
        ├── architecture-review/
        │   ├── SKILL.md
        │   └── references/
        │       ├── architect-context.md
        │       └── review-checklist.md
        ├── framework-design/
        │   ├── SKILL.md
        │   └── references/
        │       └── framework-principles.md
        └── code-review/
            ├── SKILL.md
            └── references/
                └── code-review-checklist.md
```

## 建議安裝方式

### 方式 A：套用到單一 Repository

將：

- `AGENTS.md` 複製到 Repository 根目錄。
- `.agents/skills/` 整個目錄複製到 Repository 內。

這種方式適合讓團隊共同使用，並可納入 Git。

### 方式 B：作為個人全域設定

將：

- `AGENTS.md` 複製為 `~/.codex/AGENTS.md`
- `.agents/skills/` 下的三個 Skill 目錄，複製到 `~/.agents/skills/`

Windows PowerShell 範例：

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex"
New-Item -ItemType Directory -Force "$HOME\.agents\skills"

Copy-Item ".\AGENTS.md" "$HOME\.codex\AGENTS.md" -Force
Copy-Item ".\.agents\skills\*" "$HOME\.agents\skills\" -Recurse -Force
```

## 使用方式

在 Codex 中可明確指定：

```text
$architecture-review
$framework-design
$code-review
```

也可以直接描述任務；當任務符合 Skill 的 description 時，Codex 可自動選用。

## 建議的下一步

先連續使用兩週，記錄以下情況：

1. 哪些回覆仍太偏教科書。
2. 哪些檢查項目沒有被執行。
3. 哪些輸出格式不符合實際決策習慣。
4. 哪些規則只適用設備業，哪些應提升為跨領域原則。

再依實際使用結果修改，而不是一次把所有經驗塞入單一 Skill。
