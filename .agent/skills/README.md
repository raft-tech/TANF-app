# Overview of Agent Skills

Agent skills allow AI coding assistants to dynamically discover and execute organized sets of instructions. They help save tokens by only loading detailed context when a task matches the skill's defined trigger or metadata.

## 1. Structure of an Agent Skill
A skill is represented as a project folder that contains a mandatory configuration file:
* **`SKILL.md` (Mandatory):** Located at the root of the skill folder. It must start with YAML frontmatter containing a unique `name` and a clear `description`.
* **Subdirectories (Optional):** Folders like `scripts/`, `references/`, or `assets/` to hold executables or documentation supporting the skill.

## 2. Setting Up a Custom Skill
1. **Create the Folder:** Place a new directory inside your workspace configuration path (e.g., `.github/skills/my-skill/`).
2. **Define Metadata:** Add a `SKILL.md` file and include descriptive YAML frontmatter so the AI agent knows when to activate it.
3. **Write Guidance:** Document specific steps, rules, code templates, or output formats within the markdown file.

## 3. Invoking the Skill
* **Discovery:** Type `/skills` in supported AI chat interfaces to see all available capabilities.
* **Execution:** Prompt the agent with a task that aligns with your skill's description, and the agent will load and run it automatically.
