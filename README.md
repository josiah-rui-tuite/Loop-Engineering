# The Loop Engineering Compendium

This repository serves as the official companion for *The Loop Engineering Compendium*, a technical guide on architecting and controlling autonomous AI agent systems.

## Summary
**Loop Engineering** is a technical discipline for designing, operating, and improving recursive feedback loops for AI agents. Instead of humans manually prompting agents turn-by-turn, Loop Engineering focuses on the loop itself: *Objective Discovery → Context Acquisition → Planning → Execution → Observation → Verification → Adjustment → State Preservation → Next Action/Human Handoff*.

The human role shifts from a "manual operator" (issuing instructions every turn) to a **"System Architect, Approver, and Auditor"** of automated production lines. The core thesis is that leverage has moved from "crafting individual prompts" to "designing control systems that orchestrate agents."

A common misconception is that "autonomy eliminates the need for human review." In reality, an unmanaged loop is simply an unmanaged loop that makes mistakes at scale. "Completion" is a *claim*, not a *proof*. This book provides a rigorous framework for building safe, efficient AI systems by focusing on the design of verification, permissions, state management, exit conditions, and human gates.

*(Note: The English edition of this book is currently in development and will be released in the near future.)*

## Table of Contents

### Part I — Conceptual Framework
1. Paradigm Shift
2. The Four-Layer Evolution Model
3. Origins and Genealogy
4. The Necessity of Loop Engineering
5. The Three Foundational Pillars (Prompt/Context/Harness)
6. Fundamental Loop Structures
7. Loop Contracts and Guardrails
8. DCG (Directed Cyclic Graphs) and State Synchronization
9. The 5+1 Components
10. Maker–Checker Separation

### Part II — Practical Implementation
* 22. Task List App Prototype
* 23. PatchCore Visual Inspection App
* 24. Factory Dashboard Design
* 25. Data Infrastructure Considerations
* 26. API Integration Patterns
* 27. Building MCP Servers

## Repository Structure
This repository provides the code and configuration examples referenced in the book, emphasizing the concept of "Externalizing State."

* `skills/`: Reusable AI skill definitions (SKILL.md)
* `state/`: Externalized loop states (decision_log.md, etc.)
* `security/`: Permission boundaries and denial lists (deny_commands.yaml)
* `reports/`: Execution metrics and improvement logs

## Feedback & Contribution
For bug reports, technical questions, or improvement suggestions regarding the book or the sample code, please utilize the repository's [Issues](https://github.com/josiah-rui-tuite/Loop-Engineering/issues) section. Feedback from readers is invaluable for future updates and revisions.

## Copyright & Disclaimer
This book incorporates generative AI (Large Language Models) in its composition, information gathering, and drafting processes. While the author has verified the content, no guarantees are made regarding its completeness or the functionality of the code provided.

© 2026 Josiah Rui Tuite. All rights reserved.
