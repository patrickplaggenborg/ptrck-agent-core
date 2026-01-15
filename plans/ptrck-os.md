# ptrck-os - Personal Operating System

A VPS-hosted AI assistant accessible via Telegram (and later Slack, email, web) that can answer questions directly or spawn isolated Docker containers for complex tasks requiring full Claude Code capabilities.

---

## Core Insight: Claude Agent SDK = Full Claude Code

The Claude Agent SDK **wraps Claude Code CLI** (`claude -p`), not just the raw Anthropic API:

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk';

const response = query({ prompt: "Build a REST API" });
// ↑ Spawns `claude` under the hood with ALL Claude Code tools:
// Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch, etc.
```

**Requirement:** Claude Code CLI must be installed (`npm install -g @anthropic-ai/claude-code`)

---

## Architecture: Deployed via Coolify

```
┌──────────────────────────────────────────────────────────────────┐
│                           YOUR VPS                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                         COOLIFY                              │ │
│  │  (manages container deployment, env vars, restarts, logs)   │ │
│  │                                                              │ │
│  │  ┌─────────────┐  ┌──────────────────┐  ┌───────────────┐   │ │
│  │  │  Your other │  │     ptrck-os     │  │  Other apps   │   │ │
│  │  │  apps       │  │  (Coolify app)   │  │               │   │ │
│  │  │             │  │  - Telegram bot  │  │               │   │ │
│  │  │             │  │  - Session mgmt  │  │               │   │ │
│  │  │             │  │  - Task routing  │  │               │   │ │
│  │  └─────────────┘  └────────┬─────────┘  └───────────────┘   │ │
│  └────────────────────────────┼────────────────────────────────┘ │
│                               │                                   │
│                               │ Docker socket (mounted via Coolify)
│                               ▼                                   │
│            ┌─────────────────────────────────────┐                │
│            │         TASK CONTAINERS             │                │
│            │  (spawned by ptrck-os on demand)    │                │
│            │                                     │                │
│            │  ┌───────────┐  ┌───────────┐      │                │
│            │  │  Task #1  │  │  Task #2  │ ...  │                │
│            │  │ Claude    │  │ Claude    │      │                │
│            │  │ Code CLI  │  │ Code CLI  │      │                │
│            │  │ isolated  │  │ isolated  │      │                │
│            │  │ workspace │  │ workspace │      │                │
│            │  └───────────┘  └───────────┘      │                │
│            │                                     │                │
│            │  (NOT managed by Coolify -          │                │
│            │   just Docker containers)           │                │
│            └─────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────┘
```

**How it works:**
1. **ptrck-os is deployed as a Coolify app** (from git repo)
2. **Coolify mounts Docker socket** (`/var/run/docker.sock`) into the container
3. **ptrck-os spawns task containers** via Docker API when needed
4. **Task containers are "invisible" to Coolify** - just regular Docker containers
5. **Full isolation** - each task runs in its own container with its own filesystem

---

## Two Execution Modes

### Mode 1: Quick Query (No Container)
For simple questions that don't need filesystem access:
- "What's the weather in Amsterdam?"
- "Explain how React hooks work"
- "Write a regex for email validation"
- "What's 2+2?"

**Behavior:** Answered directly via Anthropic API call. Fast, cheap, no container.

### Mode 2: Task Execution (Spawns Container)
For work requiring isolated workspace:
- "Clone my-repo and fix the failing tests"
- "Create a new React component for user profiles"
- "Review the code in github.com/user/repo"
- `/task Set up a new Express API with TypeScript`

**Triggers for container mode:**
- User explicitly uses `/task` command
- User mentions a repo URL or git operation
- User requests file creation, editing, or code execution
- Claude determines it needs filesystem/bash access

**Behavior:** Spawns isolated container with Claude Code CLI, executes task, streams results back.

---

## Message Flow

```
User sends Telegram message
            │
            ▼
┌───────────────────────────┐
│        ptrck-os           │
│    (orchestrator)         │
│                           │
│  1. Receive message       │
│  2. Classify intent       │
│     - Quick query?        │
│     - Needs workspace?    │
└─────────────┬─────────────┘
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
┌──────────┐   ┌─────────────────────┐
│  Mode 1  │   │       Mode 2        │
│  Quick   │   │  Task Execution     │
│  Query   │   │                     │
│          │   │  1. Spawn/resume    │
│  Direct  │   │     container       │
│  API     │   │  2. Clone repo      │
│  call    │   │     (if needed)     │
│          │   │  3. Run Claude      │
│          │   │     Agent SDK       │
│          │   │  4. Stream output   │
└────┬─────┘   └──────────┬──────────┘
     │                    │
     └────────┬───────────┘
              │
              ▼
┌───────────────────────────┐
│  Send response back to    │
│  Telegram                 │
└───────────────────────────┘
```

---

## Container Images

### 1. ptrck-os Orchestrator (deployed via Coolify)

```dockerfile
# docker/orchestrator/Dockerfile
FROM node:20-slim

# Install Docker CLI to control sibling containers
RUN apt-get update && \
    apt-get install -y docker.io && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# No Claude Code here - just orchestration
CMD ["npm", "start"]
```

### 2. Task Runner (spawned on demand)

```dockerfile
# docker/task-runner/Dockerfile
FROM ubuntu:24.04

# Install essentials
RUN apt-get update && apt-get install -y \
    curl git bash jq python3 python3-pip nodejs npm \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user for security
RUN useradd -m -s /bin/bash agent
USER agent
WORKDIR /home/agent

# Create workspace directory
RUN mkdir -p /home/agent/workspace

WORKDIR /home/agent/workspace

# Keep container alive for exec commands
CMD ["sleep", "infinity"]
```

---

## Project Structure

```
ptrck-os/
├── src/
│   ├── index.ts                    # Entry point, starts Telegram bot
│   │
│   ├── config/
│   │   ├── index.ts                # Configuration loader
│   │   └── env.ts                  # Zod schema for env validation
│   │
│   ├── orchestrator/
│   │   ├── classifier.ts           # Classify: quick query vs task
│   │   └── docker-manager.ts       # Spawn/manage task containers
│   │
│   ├── interfaces/
│   │   └── telegram/
│   │       ├── bot.ts              # Telegram bot setup (grammy)
│   │       ├── handlers.ts         # Message handlers
│   │       └── formatters.ts       # Response formatting
│   │
│   ├── sessions/
│   │   ├── manager.ts              # Session lifecycle
│   │   └── store.ts                # SQLite persistence
│   │
│   ├── tasks/
│   │   ├── manager.ts              # Task lifecycle
│   │   ├── state-machine.ts        # QUEUED → RUNNING → COMPLETED
│   │   └── executor.ts             # Execute in container
│   │
│   └── agents/
│       ├── quick-query.ts          # Direct API call for simple questions
│       └── container-agent.ts      # Claude Agent SDK in container
│
├── docker/
│   ├── orchestrator/
│   │   └── Dockerfile              # ptrck-os image
│   └── task-runner/
│       └── Dockerfile              # Task execution image
│
├── data/                           # Persistent data (Docker volume)
│   └── ptrck-os.db                 # SQLite database
│
├── docker-compose.yml              # Local development
├── package.json
├── tsconfig.json
└── .env.example
```

---

## Key Dependencies

```json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.0",
    "@anthropic-ai/sdk": "^0.30.0",
    "grammy": "^1.21.0",
    "dockerode": "^4.0.0",
    "better-sqlite3": "^11.0.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "typescript": "^5.4.0",
    "@types/node": "^20.0.0",
    "@types/dockerode": "^3.3.0",
    "@types/better-sqlite3": "^7.6.0"
  }
}
```

---

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...           # For Claude API calls
TELEGRAM_BOT_TOKEN=...                  # From @BotFather

# Optional - for task containers
GITHUB_TOKEN=...                        # For cloning private repos

# Database
DATABASE_PATH=/data/ptrck-os.db         # SQLite database path

# Future integrations
JIRA_EMAIL=...
JIRA_API_TOKEN=...
JIRA_CLOUD_ID=...
SLACK_BOT_TOKEN=...
```

---

## docker-compose.yml (Local Development)

```yaml
version: '3.8'

services:
  ptrck-os:
    build:
      context: .
      dockerfile: docker/orchestrator/Dockerfile
    container_name: ptrck-os
    restart: unless-stopped
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_PATH=/data/ptrck-os.db
    volumes:
      # Mount Docker socket to spawn sibling containers
      - /var/run/docker.sock:/var/run/docker.sock
      # Persistent data
      - ptrck-os-data:/data
    networks:
      - ptrck-network

networks:
  ptrck-network:
    driver: bridge

volumes:
  ptrck-os-data:
```

---

## Coolify Deployment

1. **Create new application in Coolify:**
   - Type: "Docker Compose"
   - Source: Git repository (this repo)

2. **Configure volumes in Coolify UI:**
   - Add: `/var/run/docker.sock:/var/run/docker.sock`

3. **Set environment variables in Coolify:**
   - `ANTHROPIC_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `DATABASE_PATH=/data/ptrck-os.db`

4. **Deploy**

---

## Core Code Patterns

### Intent Classifier

```typescript
// src/orchestrator/classifier.ts
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

type Intent = 'quick_query' | 'task_execution';

export async function classifyIntent(message: string): Promise<Intent> {
  // Check explicit triggers first
  if (message.startsWith('/task')) return 'task_execution';
  if (message.match(/github\.com|gitlab\.com|clone|repo/i)) return 'task_execution';
  if (message.match(/create file|edit file|run command|fix.*code/i)) return 'task_execution';

  // For ambiguous cases, use Claude to classify
  const response = await anthropic.messages.create({
    model: 'claude-haiku-3-5',
    max_tokens: 10,
    messages: [{
      role: 'user',
      content: `Classify this request. Reply ONLY with "quick" or "task".

Quick = simple question, explanation, calculation, no files needed
Task = needs file access, code execution, git operations, workspace

Request: "${message}"`
    }]
  });

  const answer = (response.content[0] as any).text.toLowerCase().trim();
  return answer.includes('task') ? 'task_execution' : 'quick_query';
}
```

### Quick Query Handler

```typescript
// src/agents/quick-query.ts
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

export async function handleQuickQuery(
  message: string,
  conversationHistory: Array<{role: string, content: string}>
): Promise<string> {

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-5-20241022',
    max_tokens: 4096,
    system: `You are ptrck-os, a helpful AI assistant. Answer questions directly and concisely.
If the user needs file operations, code execution, or a workspace, tell them to use /task.`,
    messages: conversationHistory.map(m => ({
      role: m.role as 'user' | 'assistant',
      content: m.content
    }))
  });

  return (response.content[0] as any).text;
}
```

### Docker Manager

```typescript
// src/orchestrator/docker-manager.ts
import Docker from 'dockerode';

const docker = new Docker({ socketPath: '/var/run/docker.sock' });

const TASK_RUNNER_IMAGE = 'ptrck-os-task-runner:latest';

export async function getOrCreateContainer(taskId: string): Promise<Docker.Container> {
  const containerName = `ptrck-task-${taskId}`;

  try {
    // Try to get existing container
    const container = docker.getContainer(containerName);
    const info = await container.inspect();

    if (info.State.Running) {
      return container;
    }

    // Start if stopped
    await container.start();
    return container;

  } catch (err) {
    // Container doesn't exist, create it
    const container = await docker.createContainer({
      Image: TASK_RUNNER_IMAGE,
      name: containerName,
      Tty: true,
      HostConfig: {
        Memory: 2 * 1024 * 1024 * 1024,  // 2GB limit
        CpuPeriod: 100000,
        CpuQuota: 100000,  // 1 CPU
        NetworkMode: 'bridge',
      },
      Env: [
        `ANTHROPIC_API_KEY=${process.env.ANTHROPIC_API_KEY}`,
      ],
    });

    await container.start();
    return container;
  }
}

export async function executeInContainer(
  container: Docker.Container,
  command: string[]
): Promise<{ stdout: string; stderr: string; exitCode: number }> {

  const exec = await container.exec({
    Cmd: command,
    AttachStdout: true,
    AttachStderr: true,
  });

  return new Promise((resolve, reject) => {
    exec.start({ hijack: true, stdin: false }, (err, stream) => {
      if (err) return reject(err);

      let stdout = '';
      let stderr = '';

      container.modem.demuxStream(stream,
        { write: (chunk: Buffer) => stdout += chunk.toString() },
        { write: (chunk: Buffer) => stderr += chunk.toString() }
      );

      stream.on('end', async () => {
        const info = await exec.inspect();
        resolve({ stdout, stderr, exitCode: info.ExitCode });
      });
    });
  });
}

export async function cleanupOldContainers(maxAgeHours: number = 24): Promise<void> {
  const containers = await docker.listContainers({ all: true });
  const cutoff = Date.now() - (maxAgeHours * 60 * 60 * 1000);

  for (const info of containers) {
    if (info.Names[0]?.startsWith('/ptrck-task-')) {
      const container = docker.getContainer(info.Id);
      const details = await container.inspect();
      const created = new Date(details.Created).getTime();

      if (created < cutoff) {
        await container.stop().catch(() => {});
        await container.remove();
      }
    }
  }
}
```

### Container Agent Executor

```typescript
// src/agents/container-agent.ts
import { getOrCreateContainer, executeInContainer } from '../orchestrator/docker-manager';

export async function executeTask(
  taskId: string,
  prompt: string,
  repoUrl?: string
): Promise<AsyncGenerator<string>> {

  const container = await getOrCreateContainer(taskId);

  // Clone repo if provided
  if (repoUrl) {
    await executeInContainer(container, [
      'git', 'clone', repoUrl, '/home/agent/workspace/repo'
    ]);
  }

  // Create agent script
  const agentScript = `
    const { query } = require('@anthropic-ai/claude-agent-sdk');

    (async () => {
      const response = query({
        prompt: ${JSON.stringify(prompt)},
        options: {
          model: 'claude-sonnet-4-5',
          workingDirectory: '/home/agent/workspace${repoUrl ? '/repo' : ''}',
          permissionMode: 'bypassPermissions',  // Safe in isolated container
          allowedTools: [
            'Read', 'Write', 'Edit', 'Bash',
            'Grep', 'Glob', 'WebFetch', 'WebSearch'
          ]
        }
      });

      for await (const msg of response) {
        // Output each message as JSON line for parsing
        console.log(JSON.stringify(msg));
      }
    })().catch(err => {
      console.error(JSON.stringify({ type: 'error', error: err.message }));
      process.exit(1);
    });
  `;

  // Execute and stream results
  const result = await executeInContainer(container, [
    'node', '-e', agentScript
  ]);

  return parseAgentOutput(result.stdout);
}

async function* parseAgentOutput(output: string): AsyncGenerator<string> {
  const lines = output.split('\n').filter(Boolean);

  for (const line of lines) {
    try {
      const msg = JSON.parse(line);

      if (msg.type === 'assistant' && typeof msg.content === 'string') {
        yield msg.content;
      } else if (msg.type === 'tool_call') {
        yield `🔧 Executing: ${msg.tool_name}...`;
      } else if (msg.type === 'error') {
        yield `❌ Error: ${msg.error}`;
      }
    } catch {
      // Skip non-JSON lines
    }
  }
}
```

### Telegram Bot

```typescript
// src/interfaces/telegram/bot.ts
import { Bot, Context } from 'grammy';
import { classifyIntent } from '../../orchestrator/classifier';
import { handleQuickQuery } from '../../agents/quick-query';
import { executeTask } from '../../agents/container-agent';
import { SessionStore } from '../../sessions/store';

const bot = new Bot(process.env.TELEGRAM_BOT_TOKEN!);
const sessions = new SessionStore();

bot.command('start', async (ctx) => {
  await ctx.reply(
    `Welcome to ptrck-os! 🤖\n\n` +
    `I can help you with:\n` +
    `• Questions and explanations (just ask)\n` +
    `• Code tasks in isolated containers (use /task)\n\n` +
    `Try: "Explain async/await" or "/task Clone github.com/user/repo and run tests"`
  );
});

bot.command('task', async (ctx) => {
  const prompt = ctx.message?.text?.replace('/task', '').trim();
  if (!prompt) {
    await ctx.reply('Usage: /task <description>\n\nExample: /task Clone my-repo and fix the failing tests');
    return;
  }

  await ctx.reply('🚀 Starting task in isolated container...');

  const taskId = `${ctx.chat.id}-${Date.now()}`;

  try {
    for await (const chunk of executeTask(taskId, prompt)) {
      await ctx.reply(chunk);
    }
    await ctx.reply('✅ Task completed!');
  } catch (err) {
    await ctx.reply(`❌ Task failed: ${err.message}`);
  }
});

bot.on('message:text', async (ctx) => {
  const message = ctx.message.text;
  const chatId = ctx.chat.id.toString();

  // Get or create session
  const session = sessions.getOrCreate(chatId);
  session.addMessage('user', message);

  // Classify intent
  const intent = await classifyIntent(message);

  if (intent === 'quick_query') {
    // Direct answer
    await ctx.reply('💭 Thinking...');
    const response = await handleQuickQuery(message, session.history);
    session.addMessage('assistant', response);
    await ctx.reply(response);

  } else {
    // Needs container
    await ctx.reply(
      '🔧 This looks like it needs a workspace.\n' +
      'Use `/task` to run it in an isolated container.\n\n' +
      `Example: /task ${message}`
    );
  }
});

export { bot };
```

---

## Task State Machine

```
QUEUED ──────▶ RUNNING ──────▶ COMPLETED
                  │
                  ├──▶ AWAITING_INPUT ──▶ RUNNING
                  │     (user needs to provide info)
                  │
                  └──▶ FAILED ──▶ (can retry) ──▶ QUEUED
```

---

## Implementation Phases

### Phase 1: MVP ✨
**Goal:** Telegram bot with two-mode execution

- [ ] Initialize TypeScript project
- [ ] Build orchestrator Dockerfile
- [ ] Build task-runner Dockerfile
- [ ] Implement Telegram bot (grammy)
- [ ] Implement intent classifier
- [ ] Implement quick query handler (direct API)
- [ ] Implement Docker manager
- [ ] Implement container agent executor
- [ ] Basic SQLite session storage
- [ ] Test locally with docker-compose

**Deliverable:** Send Telegram message → classified → direct answer OR task in container

### Phase 2: Session & State Management
- [ ] Full session persistence across restarts
- [ ] Task state machine
- [ ] Container lifecycle management (cleanup old)
- [ ] Progress reporting to user
- [ ] Resume interrupted tasks

### Phase 3: Skill Integration
- [ ] Mount existing skills into task containers
- [ ] Skill activation in system prompt
- [ ] Custom MCP tools (Jira, Confluence, etc.)

### Phase 4: Multi-Interface
- [ ] Slack adapter
- [ ] Email adapter (IMAP/SMTP)
- [ ] Cross-interface conversation binding

### Phase 5: Multi-Agent
- [ ] Subagent definitions (Planner, Implementer, Reviewer)
- [ ] Multi-agent orchestration
- [ ] Review loop handling

### Phase 6: Production
- [ ] Health checks
- [ ] Monitoring & alerting
- [ ] Backup system
- [ ] Cost tracking (API usage)

---

## Verification Tests

1. **Quick Query Test:**
   - Send: "What's 2+2?"
   - Expect: Direct answer, no container spawned

2. **Task Container Test:**
   - Send: "/task Create a file hello.txt with 'Hello World'"
   - Expect: Container spawned, file created inside container, not on host

3. **Isolation Test:**
   - Start two tasks in parallel
   - Verify: Each runs in separate container, no interference

4. **Persistence Test:**
   - Start conversation, ask follow-up questions
   - Restart ptrck-os
   - Verify: Can continue conversation

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Container escape | Non-root user, drop capabilities |
| Resource exhaustion | Memory/CPU limits per container |
| Secrets in tasks | Only pass ANTHROPIC_API_KEY to task containers |
| Docker socket | Only ptrck-os container has access |
| Network access | Containers have bridge network (can be restricted) |

---

## Getting Started (for clean handoff)

```bash
# 1. Clone repo
git clone <repo-url>
cd ptrck-os

# 2. Install dependencies
npm install

# 3. Copy env file and fill in values
cp .env.example .env
# Edit .env with ANTHROPIC_API_KEY and TELEGRAM_BOT_TOKEN

# 4. Build task-runner image
docker build -t ptrck-os-task-runner:latest -f docker/task-runner/Dockerfile .

# 5. Start with docker-compose
docker-compose up -d

# 6. Test by messaging your Telegram bot
```

---

## Files to Create (Implementation Order)

1. `package.json` - Dependencies
2. `tsconfig.json` - TypeScript config
3. `.env.example` - Environment template
4. `docker/task-runner/Dockerfile` - Task runner image
5. `docker/orchestrator/Dockerfile` - Orchestrator image
6. `docker-compose.yml` - Local dev setup
7. `src/config/env.ts` - Environment validation
8. `src/config/index.ts` - Config loader
9. `src/sessions/store.ts` - SQLite session storage
10. `src/orchestrator/classifier.ts` - Intent classification
11. `src/orchestrator/docker-manager.ts` - Container management
12. `src/agents/quick-query.ts` - Direct API handler
13. `src/agents/container-agent.ts` - Container execution
14. `src/interfaces/telegram/bot.ts` - Telegram bot
15. `src/index.ts` - Entry point
