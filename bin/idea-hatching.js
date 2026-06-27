#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');

const repoRoot = path.resolve(__dirname, '..');
const defaultTarget = path.join(os.homedir(), '.claude', 'skills', 'idea-hatching');
const defaultWorkspace = path.join(os.homedir(), 'idea-hatching');
const COPY_ENTRIES = ['SKILL.md', 'README.md', 'references', 'scripts', 'templates'];

function usage() {
  console.log(`Usage:
  idea-hatching install [--target <dir>] [--no-init]

Default:
  idea-hatching install

Installs the Claude Code skill to ~/.claude/skills/idea-hatching and initializes ~/idea-hatching.
Auto Mode is not enabled by install; configure it manually after installation.`);
}

function parseArgs(argv) {
  const first = argv[2];
  const args = { command: (!first || first === '--help' || first === '-h') ? (first ? 'help' : 'install') : first, target: defaultTarget, init: true };
  for (let i = 3; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--target') {
      args.target = path.resolve(argv[++i]);
    } else if (a === '--no-init') {
      args.init = false;
    } else if (a === '--help' || a === '-h') {
      args.command = 'help';
    } else {
      throw new Error(`Unknown argument: ${a}`);
    }
  }
  return args;
}

function rmrf(p) {
  fs.rmSync(p, { recursive: true, force: true });
}

function copyRecursive(src, dest) {
  const st = fs.statSync(src);
  if (st.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const child of fs.readdirSync(src)) {
      if (child === '.git' || child === 'node_modules') continue;
      copyRecursive(path.join(src, child), path.join(dest, child));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function initWorkspace() {
  fs.mkdirSync(defaultWorkspace, { recursive: true });
  const index = path.join(defaultWorkspace, 'INDEX.md');
  if (!fs.existsSync(index)) {
    fs.writeFileSync(index, `# Idea Hatching · Index\n\n> Catalog of incubating ideas, one row each. status: incubating / hatched / blocked (fatal contradiction).\n> F = feasibility (0–3, cost vs benefit)   C = credibility (0–3, coverage + referenceability)\n\n| slug | status | F | C | last advanced | one-liner |\n|------|--------|---|---|---------------|-----------|\n`, 'utf8');
  }
  const heartbeat = path.join(defaultWorkspace, 'heartbeat.json');
  if (!fs.existsSync(heartbeat)) {
    const template = path.join(repoRoot, 'templates', 'heartbeat.json');
    fs.copyFileSync(template, heartbeat);
  }
}

function install(args) {
  fs.mkdirSync(args.target, { recursive: true });
  for (const entry of COPY_ENTRIES) {
    const src = path.join(repoRoot, entry);
    const dest = path.join(args.target, entry);
    rmrf(dest);
    copyRecursive(src, dest);
  }
  if (args.init) initWorkspace();
  console.log(`Installed Idea Hatching skill to ${args.target}`);
  if (args.init) console.log(`Initialized workspace at ${defaultWorkspace}`);
  console.log('Auto Mode is not enabled. Configure it manually after installation.');
}

function main() {
  try {
    const args = parseArgs(process.argv);
    if (args.command === 'help') return usage();
    if (args.command !== 'install') throw new Error(`Unknown command: ${args.command}`);
    install(args);
  } catch (err) {
    console.error(`idea-hatching: ${err.message}`);
    usage();
    process.exit(1);
  }
}

main();
