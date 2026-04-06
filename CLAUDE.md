# Session Bootstrap

## Output Rules
- Answer is always line 1 — no openers ("Sure!", "Great!", "Absolutely!")
- No closings ("I hope this helps!", "Let me know!")
- Never restate the prompt — execute immediately
- ASCII only — no em dashes, smart quotes, Unicode
- No "As an AI..." framing
- No disclaimers unless genuine safety risk
- No unsolicited suggestions — exact scope only
- Simplest working solution — no over-engineering
- If uncertain → say "I don't know", never guess
- If user corrects → that correction is session ground truth
- Never read the same file twice
- Never touch code outside the request scope
- Answer only in russian

## Stack & Tools
- RTK installed on VPS (ssh host: `vps`) — use for all remote commands
- context-mode MCP active locally — use sandbox tools for heavy data

## Project Context
- Codebase: local Windows 11, Claude Code Desktop
- Deploy target: VPS Ubuntu, Docker Compose
- Goal: refactoring + deploy testing

## Rules — Remote Commands via RTK
Always prefix VPS commands with rtk over SSH:

### Docker
- `ssh vps "rtk docker compose logs --tail=100 <service>"`
- `ssh vps "rtk docker compose ps"`
- `ssh vps "rtk docker compose up -d --build"`
- `ssh vps "rtk docker logs <container>"`
- `ssh vps "rtk docker images"`

### Git (on VPS)
- `ssh vps "rtk git status"`
- `ssh vps "rtk git log -n 10"`
- `ssh vps "rtk git diff"`
- `ssh vps "rtk git pull"`

### Files & Search (on VPS)
- `ssh vps "rtk ls /path/to/project"`
- `ssh vps "rtk grep 'pattern' /path/to/project"`
- `ssh vps "rtk find '*.log' /var/log"`
- `ssh vps "rtk read /path/to/file.conf"`

### Logs & System (on VPS)
- `ssh vps "rtk log /var/log/app.log"`
- `ssh vps "rtk curl http://localhost:8080/health"`
- `ssh vps "rtk env -f APP"`

### Test Runners (on VPS)
- `ssh vps "rtk pytest"`
- `ssh vps "rtk go test"`
- `ssh vps "rtk cargo test"`

Never run any of these without rtk prefix on VPS.

## Rules — Heavy Data
- Any output or file >10KB → ctx_execute_file, never read raw
- Repeated file reads → ctx_read (cached), never Read tool twice on same file
- After each deploy test → ctx_index the result summary

## Rules — Session Memory
- Before starting a task → ctx_search for relevant prior context
- After resolving an error → ctx_index: service name, root cause, fix applied
- After architecture decision → ctx_index: what changed and why

## Session Start Checklist
Run these now:
1. `ctx_search "deploy status"` — restore prior context
2. `ssh vps "rtk docker compose ps"` — current container state
3. `ssh vps "rtk git log -n 5"` — recent changes on VPS
4. Report findings, then ask what to work on
