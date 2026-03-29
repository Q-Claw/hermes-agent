# Example Gateway Hooks

Ready-to-use hooks you can copy into `~/.hermes/hooks/` to extend gateway behavior.

## Available Examples

### boot-md

Run a `BOOT.md` checklist on every gateway startup. Drop a markdown file at
`~/.hermes/BOOT.md` with instructions for the agent to execute — startup health
checks, notifications, task resumption, etc.

**Install:**

```bash
cp -r gateway/example-hooks/boot-md ~/.hermes/hooks/boot-md
```

**Usage:**

Create `~/.hermes/BOOT.md`:

```markdown
# Startup Checklist

1. Check if any cron jobs failed overnight — run `hermes cron list`
2. Send a message to Discord #general saying "Gateway restarted, all systems go"
```

The agent runs these instructions in a background session on every gateway restart.
If nothing needs attention, it stays silent.

## Creating Your Own Hooks

See the [Event Hooks documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks)
for the full guide on creating custom hooks.
