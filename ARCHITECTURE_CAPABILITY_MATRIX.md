# Architecture Capability Matrix

| Capability | Bento source | CloudBox repository | Qt IC tools | Equipment systems |
|---|---|---|---|---|
| Frontend architecture | Source-verified | Engine UI/components | User-stated | Current practice |
| Backend/application services | Source-verified | Not primary | Tool services | Current practice |
| Client/Server | Source-verified | Limited/native services | User-stated | Current practice |
| API/protocol contracts | Source-verified HTTP | Native/platform APIs | Hardware/tool protocols | Industrial protocols |
| Data/transaction design | Source-verified | Save/config/resource state | User-stated | Recipe/history/state |
| Cross-platform native | Not primary | Repository-verified | User-stated | Windows/IPC focus |
| Rendering/engine loop | Not primary | Repository-verified | Not primary | UI/pipeline analogies only |
| Platform adapters | Deployment targets | Repository-verified | User-stated | Device/PLC adapters |
| Safe incremental refactor | Source-verified | Historical refactors | User-stated | Current practice |
| Recovery/lifecycle | Source-verified persistence | Repository-verified app/resource lifecycle | User-stated | Current practice |
| Deployment/operations | Source-verified | Multi-platform packaging | User-stated | Current practice |
| Quality/process governance | Source-verified | Historical release log | User-stated | Current practice |

## Usage Rule

Use the matrix to select relevant prior experience, not to force a common architecture across all domains.
