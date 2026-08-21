# CloudBox Skills 發展地圖

- 文件 ID：CBX-MAP-001
- 版本：0.1
- 狀態：目前狀態與路線總覽（informative view）
- 更新日期：2026-08-17（Asia/Taipei）
- 觀察基準：`main` / `origin/main`，commit `e35c8f0`
- 最新正式 tag：`v7.6.24`；目前 `main` 比該 tag 多 8 個 commits
- 文件 owner：CloudBox Skills 維護者
- 權威性：本文件是跨文件的導航與狀態視圖；各項 mutable fact 仍以列出的 registry、Eval、Git tag 與 release evidence 為準

## 1. 目的與範圍

本文件回答四個問題：

1. CloudBox Skills 現在有哪些能力層？
2. Skill 如何分類、評估、演化與分發？
3. 目前哪些部分已完成，哪些仍是實驗或 deferred？
4. 下一階段應先補 release、lifecycle、Eval、Hooks 或新產品領域的哪一部分？

本文件不是第二份 Skill registry，也不是第二份 lifecycle registry。分類以 `config/skill-domain-catalog.json` 與 `docs/SKILL_TAXONOMY.md` 為準；分發以 `config/skill-distribution.json` 為準；lifecycle template 以 `config/lifecycle-templates.json` 為準。

## 2. 一頁架構圖

```text
使用者／Agent 任務
        ↓
Skill routing：using-cloudbox-skills + flat manifest
        ↓
Skill instructions + declared references
        ↓
模型產生工程交付物
        ↓
Eval：routing / behavior / runtime / grader
        ↓
Lifecycle：RED → change → GREEN → regression → review
        ↓
Release evidence：版本、插件、CI、安裝、限制與回滾資訊
        ↓
Core public 或私有子分類分發（private-meta／private-game／private-equipment／private-operation／private-art）
        ↓
learn：保留修正、失敗模式與下一個案例

未來補入的 Hooks：在 Agent lifecycle 邊界做觸發、防護、提醒與快速檢查；不擁有 Skill lifecycle 狀態。
```

圖的觀點是「Skill 演化與分發控制流」，不是部署圖；箭頭表示主要邏輯順序，不表示所有執行都同步或由同一程序完成。`config/`、`evals/`、Git release 與 release evidence 才是各自領域的來源。

## 3. 目前狀態快照

| 項目 | 目前觀察 | 來源／限制 |
|---|---:|---|
| canonical Skills | 29 | `.agents/skills/` 目錄快照；新增 Skill 後需重新計數 |
| lifecycle `active` | 27 | 各 canonical `lifecycle.json` 快照 |
| lifecycle `experimental` | 2 | 目前為 `runtime-evaluation-engineering`、`teach-while-building` |
| public Core distribution | 19 | `config/skill-distribution.json` |
| private `evolution-pack` | 10 | 包含 Skill 演化工具、Runtime Eval 與產品／遊戲 Skills |
| Behavior case files | 34 | `evals/behavior/cases/`；case 存在不等於已執行模型 |
| Runtime case files | 8 | `evals/runtime/cases/` |
| implemented lifecycle templates | 3 | `lightweight-change`、`bounded-feature`、`skill-evolution` |
| deferred lifecycle templates | 7 | 不得因名稱相似而自動 fallback |
| Agent Hooks | 0 個 repo hook 配置 | 目前未納入 Codex／Claude plugin；`.git/hooks/` 不算 Agent Hooks |

以上是 `e35c8f0` 的狀態快照，不是永久數字。新增 Skill、case、template 或 plugin projection 後，應更新本文件或建立新的狀態快照。

## 4. 能力與產品領域

### 4.1 Capability layer

目前能力層包括：

- `agent-dev`：Agent 任務契約、工具、記憶、編排、guardrail。
- `architecture-dev`：系統邊界、分散式設計、framework 與平台契約。
- `integration-dev`：外部系統 adapter、版本能力、同步與 reconciliation。
- `game-engine-dev`：遊戲／圖形引擎、場景、render、resource、input、平台 adapter。
- `platform-native-dev`：原生 OS lifecycle、裝置整合、封裝與相容性。
- `equipment-dev`：半導體設備語意、控制與 domain modeling。
- `code-change-dev`：code review、brownfield refactor、相容性與 recovery。
- `quality-dev`：品質情境、指標、證據、測試與 release gate。
- `governance-dev`：文件、流程、lifecycle、handoff 與 ownership。
- `skill-eval-dev`：Skill authoring、routing、behavior／runtime Eval 與 Skill composition。
- `learning-dev`：在實際工程工作中建立可保留的理解。

### 4.2 Product-domain layer

目前投入最深的是遊戲產品線：

```text
game-dev       legacy archaeology、gameplay、state、level、modernization
cloudbox-dev   CloudBox-first migration 與跨平台 runtime
ios-dev        native iOS rewrite 與 platform compatibility
art-dev        source、density、viewport、upscale、redraw、export
product-dev    scope、priority、economy、product evolution
marketing-dev  目前只有候選方向，尚無正式 Skill
qa-dev         characterization、replay、device、asset、release gate
```

目前遊戲私有 Skill 產品鏈：

```text
legacy-game-product-archaeology
  → gameplay-core-modernization
  → cloudbox-game-migration / native-ios-game-rewrite
  → game-asset-resolution-audit
  → indie-game-product-evolution
  → game-quality-and-release-gates
```

這條鏈是「舊產品精神續作／重寫」的專用能力，不代表一般遊戲開發必須依序載入所有 Skill。順序也不是固定的：`SKILL_ROUTING_PLAYBOOK.md` 已明講，若請求本質是 scope／monetization 決策，`indie-game-product-evolution` 應提前於技術重寫之前判斷，不必等到鏈末端才回頭決定要不要做、要不要收費——上圖畫成單線只是為了呈現典型技術產出順序，不是決策順序的權威描述。

## 5. Skill lifecycle

正式 Skill lifecycle 為：

```text
draft → experimental → active → stable → deprecated
```

目前 Skill evolution 的實作流程為：

```text
analyze
  → verify_red
  → implement
  → verify_green
  → release
  → learn
```

必要證據包括：

- sanitized、deduplicated evidence inventory
- RED baseline
- 最小修改
- GREEN 與 adjacent regression
- review／release-boundary decision
- durable state reconciliation

Lifecycle template 的 authoritative registry 是 [`config/lifecycle-templates.json`](../config/lifecycle-templates.json)；人類可讀說明在 [`LIFECYCLE_TEMPLATE_CATALOG.md`](LIFECYCLE_TEMPLATE_CATALOG.md)。

## 6. Eval 與證據閉環

CloudBox 的 Eval 分成多層：

```text
Repository/static
  → Provider execution
  → Routing
  → Behavior
  → Refinement（可選）
  → Review bundle
  → Release decision
```

需要分開理解：

- case file：定義要測什麼。
- schema／validator：確認結構正確。
- runtime execution：實際呼叫模型。
- grader：依 rubric 評分。
- RED/GREEN：判斷候選修改是否產生可觀察差異。
- release evidence：記錄模型、環境、限制與正式判斷。

`evals/behavior/` 明確規定每個 Skill 至少需要 recognition、application、counterexample；行為宣稱需要 RED baseline 與 GREEN candidate。`evals/runtime/` 則負責把 router context、selected Skill、provider、context budget、raw output 與 grader 串起來。

目前的主要限制：部分 Skill 的 application evidence 仍只涵蓋一種 archetype；deterministic rubric 主要量測證據覆蓋，不等同完整語意正確或真實產品結果；provider-backed、CI、安裝與實機結果必須逐案查證，不能由 Skill 存在推導。

## 7. 分發與版本狀態

```text
core
  = 泛化、可公開、無私有產品／敏感演化資料

private-meta
  = 私有、自我指涉：Skill 演化工具、Runtime Eval

private-game / private-equipment / private-operation / private-art
  = 私有或暫緩公開：遊戲／設備／營運行銷／美術 Skills，按內容領域分類
  （2026-08-18 起由單一 evolution-pack tier 拆分而來）
```

觀察基準是 `e35c8f0`（見文件開頭），但這是一份快照，不是永久事實——這份文件自己被 commit 進去之後，`main` 就已經往前移動；讀者應以 `git rev-parse main`／`git describe --tags` 的即時結果為準，不要把本節的 commit 名稱當成目前狀態的斷言。最新 annotated tag 仍為 `v7.6.24`。因此：

- `v7.6.24` 是最後正式 immutable release baseline。
- `main` 是包含後續 `indie-game-product-evolution` active promotion 等變更的開發 tip，且會持續往前移動。
- 在下一個版本 tag、CI、plugin install smoke test、post-release record 完成前，不應把目前 tip 稱為下一個正式 release。

公開／私有 export 的唯一分發權威是 [`config/skill-distribution.json`](../config/skill-distribution.json)。

## 8. Hooks 的位置

Hooks 尚未建立為 CloudBox Skills 的正式 repo 層。未來可採：

```text
PreToolUse   workspace、secret、protected-path、side-effect guard
PostToolUse  diff check、schema／static validator、evidence reminder
PostCompact  重新注入 handoff、lifecycle checkpoint、canonical paths
SessionStart 顯示 branch、版本與目前工作狀態
```

Hooks 不應：

- 擁有 durable lifecycle state。
- 複製 `config/lifecycle-templates.json` 的規則。
- 取代 Runtime Eval 或 grader。
- 自動 commit、tag、push 或 release。
- 把中間狀態描述成正式完成。

應由 lifecycle orchestration 擁有狀態，由 Eval 擁有驗證證據，Hooks 只做觸發、防護、提醒與快速檢查。

## 9. 跨 Agent 發展注意事項

`Skill → Hook → Eval` 是概念上的分層，不是所有 Agent 都能直接共用的固定實作管線。發展 CloudBox 時，必須把可移植核心與平台 adapter 分開：

```text
portable core
  SKILL.md、references、一般 scripts
  Eval cases、schemas、rubrics、release gate 原則

platform adapters
  Codex／Claude／Qwen 的 Hook 設定
  CLI runner、輸出解析、權限與認證
  plugin manifest、安裝與 reload 流程
```

### 9.1 可共用與不可直接共用

| 元件 | 跨 Agent 策略 | 發展時的注意事項 |
|---|---|---|
| Skill／`SKILL.md` | 優先共用 | 不要把 Codex、Claude 或特定模型的專有欄位寫成必要條件 |
| references／一般 scripts | 優先共用 | 優先使用可攜的 shell／Python；平台路徑、認證與 GUI 操作放 adapter |
| Eval cases／schemas／rubrics | 共用契約 | 必須記錄 provider、model、版本、context、工具與權限，不能只比較分數 |
| Eval runner | 平台 adapter | Codex、Claude、Ollama、Qwen 的 CLI、輸出格式與失敗狀態不可假設相同 |
| Hook 腳本邏輯 | 部分共用 | 安全檢查可共用，但輸入 JSON、exit code、事件名稱需由 adapter 接收 |
| Hook 註冊與 lifecycle event | 不直接共用 | Codex、Claude 與其他 Agent 的設定位置、事件與 trust／permission 模型不同 |
| Plugin packaging | 平台專屬 | manifest、marketplace、symlink／regular file、安裝與 reload 必須分開驗證 |

### 9.2 發展規則

- 核心 Skill 不應依賴 Hook 才能正確工作；沒有 Hook 的 Agent 仍應得到可理解且安全的降級行為。
- Hook 不得被當成 universal API；先建立中立腳本，再建立 Codex／Claude／其他 Agent 的薄 adapter。
- Eval case 與 rubric 可共用，但不同 Agent 的執行結果不能直接視為同一實驗；應保存模型、provider、context budget、工具可用性、權限模式與原始輸出。
- 同一個 Skill 在不同 Agent 上通過，不代表跨 Agent 相容性已證明；至少需要各平台安裝、routing、behavior 與權限邊界證據。
- 不把平台特有的 prompt、hook frontmatter、CLI flag 或 plugin manifest 複製進 portable Skill，避免核心污染與跨平台漂移。
- Provider／Hook 缺失、認證失敗、unsupported event 與 runtime crash 必須分類為 adapter／infrastructure failure，不得直接判定 Skill 品質失敗。
- Secrets、endpoint、帳號、provider profile 與本機 Hook 設定留在 local／SecretStore；不得因跨平台便利而寫入 Skill、Eval case 或 public export。
- 每新增一個 Agent adapter，都要補 portability check、安裝 smoke test、最小 routing／behavior case，以及明確列出未支援的事件與功能。

### 9.3 CloudBox 建議目錄邊界

```text
cloudbox-skills/
├── .agents/skills/       # portable canonical Skill source
├── evals/                 # portable evaluation contracts
├── scripts/               # shared validators plus provider adapters
├── hooks/                 # future neutral hook logic, if needed
├── .codex/                # Codex-specific hook/config adapter
├── .claude/               # Claude-specific hook/config adapter
└── private-plugin/        # private projection and packaging evidence
```

這個目錄圖是邊界建議，不代表目前所有目錄都已建立；目前 repo 尚未有正式 Agent Hook 配置。

## 10. 優先發展路線

### P0：封版目前 main 的正式 release

- exact-tip full deterministic checks。
- CI validation。
- Codex／Claude plugin install smoke test。
- 版本、annotated tag、GitHub Release 與 post-release record。
- 確認 Core export 不包含任何私有 tier 內容。
- 已知具體 blocker：`docs/releases/7.6.24-pre-release-evidence.md` 記錄 `skill-creator` quick validator 因為 `yaml`/PyYAML 在目前 Python runtime 不可用而無法啟動；exact-tip full deterministic checks 必須先確認這條路徑，不能只靠原生 validator 通過就視為已解決。

### P1a：補強 Eval 的廣度與語意品質（P1 內優先於 P1b）

- 為 `indie-game-product-evolution` 增加第二種 product archetype。
- 持續增加 adjacent regression，降低 Skill overlap 造成的假陽性。
- 對 deterministic keyword rubric 增加更強的語意或人工審查證據。
- 讓每個新 Skill 都有真正可追溯的 RED/GREEN，而不只擁有 case file。

### P1b：補齊常用 lifecycle（P1 內次於 P1a——先擴 Eval 廣度，template 才有可信的驗證基礎）

優先考慮 `release`、`hotfix`、`brownfield-refactor`、`incident-recovery`；每個 template 都需要自己的 RED、contract、validator 與 behavior evidence，不能從既有 template 靜默 fallback。

### P2a：加入最小 Hooks 層（P2 內優先於 P2b）

先做 `PreToolUse` 安全防護、`PostToolUse` 快速驗證與 `PostCompact` context recovery；等 lifecycle 與 release 基線穩定後再實作。

### P2b：擴展產品領域（P2 內次於 P2a——Hooks 是跨領域基礎設施，新產品領域可以晚一步）

- `game-art-pipeline`
- `game-marketing-and-monetization`
- 非遊戲 legacy archaeology
- 非遊戲 release-readiness／migration
- 安全分析與 threat modeling

新領域預設先進 private candidate，完成去識別化、owner／overlap review 與完整 Eval 後再考慮 Core。

## 11. 未解決事項與重訪條件

| ID | 未解決事項 | 重訪條件 |
|---|---|---|
| MAP-R01 | `main` 已超過 `v7.6.24`，下一個正式版本尚未封版 | P0 release gates 完成 |
| MAP-R02 | handoff、release history 與最新 main 狀態可能不同步 | 每次 evolution increment 結束時更新 |
| MAP-R03 | Core router 在 public-only 安裝時不能路由到 private Skill | public/private split 實際執行時驗證 |
| MAP-R04 | 部分 behavior evidence 仍只有單一 archetype | 新增第二種 application case 並完成 RED/GREEN |
| MAP-R05 | provider-backed OpenProject／Redmine 執行仍未實測 | 提供隔離測試 instance 與非正式 credential |
| MAP-R06 | Agent Hooks 尚無跨 Codex／Claude 的 adapter 設計 | lifecycle 與 release 基線穩定後建立最小 PoC |
| MAP-R07 | Skill／Eval 契約可攜，但 runner、Hook、plugin 介面尚未形成 adapter matrix | 新增 Agent provider 時完成 portability／install／routing／behavior evidence |
| MAP-R08 | 兩份文件都用「單一檔案持續累加敘事」模式，寫法本身沒變，之後都會持續重演成長問題：(1) `CLOUDBOX_SKILLS_AGENT_HANDOFF.md`，2026-08-18 已因長到 1898 行／110KB 做過一次手動歸檔（見 `docs/history/AGENT_HANDOFF_ARCHIVE.md`）；(2) `docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`（2026-08-18 稽核發現，尚未處理）——2781 行／159KB，回溯到 2026-08-08，結尾「Maintenance rule」明文規定「每次新 increment 都在最上面加一筆」，且是 `AGENTS.md` Read order 第 4 項與 `validate_evolution_handoff.py` 必查 marker 檔案，強制載入成本比 handoff 更高。次要觀察：`CHANGELOG.md`（1476 行／87KB，61 個版本，非強制閱讀，`docs/history/RELEASES.md` 已明講改查它，急迫性較低）；`*-workspace/` 資料夾（`safe-incremental-refactoring-workspace/` 已有 iteration-1/iteration-2/skill-snapshot 等疊代快照，屬於「累積目錄」而非「單一文件變胖」，可能是刻意保留、未必是缺陷）；本表（MAP-R 表）自己也沒有明文的 resolved 後移除規則，目前僅 8 筆，暫不急迫。提議的根治方案（handoff／change-history 通用）：改成「每個 increment 各自獨立成檔（沿用 `docs/releases/`／`docs/evolution/` 現有模式）＋ 該文件只放一行索引（日期、版本／slug、一句話、連結）」，成長成本從 O(整段敘述) 降到 O(一行)，之後不需要再手動歸檔。**2026-08-18 已加上機制性 guardrail**：`scripts/validate_evolution_handoff.py`（既有腳本，未另開新檔）新增 `LIVING_DOC_BUDGET_BYTES` 檢查——`CLOUDBOX_SKILLS_AGENT_HANDOFF.md` 設 20,000 bytes 活動預算，`docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md` 用「凍結上限」鎖在稽核當下的 159,084 bytes（零成長空間，不是永久豁免），超標會讓 CI 直接 FAIL，概念上比照 `scripts/validate_skill_context_budget.py` 的 `GRANDFATHERED_CEILINGS` 做法。這解決了「規則沒有強制力」的問題，但索引化重寫本身仍未實作，`docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md` 仍是 159KB 的凍結狀態，不是已經修好。 | 下次規劃大範圍多步驟工作之前先設計並實作索引化重寫；凍結上限本身不需要觸發條件，已經在運作 |

## 12. 來源與更新規則

本文件是導航視圖，不取代以下權威來源：

- 分類：`config/skill-domain-catalog.json`、`docs/SKILL_TAXONOMY.md`
- 分發：`config/skill-distribution.json`
- Lifecycle registry：`config/lifecycle-templates.json`
- Routing：`evals/skill-routing-cases.csv` 與 `SKILL_MANIFEST.json`
- Behavior／Runtime Eval：`evals/behavior/`、`evals/runtime/`
- 演化理由：`docs/CLOUDBOX_SKILLS_CHANGE_HISTORY.md`
- 當前交接：`CLOUDBOX_SKILLS_AGENT_HANDOFF.md`
- immutable release：Git commits、annotated tags、`docs/releases/`

每次新增 Skill、變更 distribution、promotion、lifecycle template、Eval contract、正式 tag 或重大 Hook 設計時，應更新本文件的狀態快照或在 change history 明確指出未更新原因。
