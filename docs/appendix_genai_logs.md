# GenAI Usage Summary

**Module:** COMP3011 – Web Services and Web Data  
**Student:** Nathaniel Sebastian (sc232ns)  

---

## Tools Declared

| Tool | Purpose |
|------|---------|
| **Google Gemini (Antigravity)** | Primary – architecture, coding, debugging |
| **ChatGPT (GPT-4)** | Secondary – feedback interpretation |

---

## Summary of Sessions

| # | Topic | AI Contribution | My Decision |
|---|-------|-----------------|-------------|
| 1 | Architecture | Layered design pattern | Adopted for project |
| 2 | RSVP Model | Separate table vs embedded | Chose relational approach |
| 3 | Auth | JWT vs sessions trade-offs | JWT for simplicity |
| 4 | Migrations | SQLite batch_alter_table | Fixed all migrations |
| 5 | Testing | Fixture isolation pattern | Enhanced with rollbacks |
| 6 | Analytics | Trending score formula | Implemented with params |
| 7 | Timezone bug | Missing import fix | Applied immediately |
| 8 | PDF generation | Puppeteer approach | Generated all PDFs |

---

## Full Conversation Logs

**See:** [docs/GENAI_EXPORT_LOGS.md](GENAI_EXPORT_LOGS.md)

This file contains detailed excerpts from 8 AI-assisted development sessions, including:
- Exact prompts given to AI tools
- AI responses (summarised)
- My decisions and implementations
- Bugs introduced and fixed

---

## Critical Evaluation

AI was used as a **development partner**, not an author:
- All suggestions were reviewed and tested before committing
- Security issues (hardcoded secrets) caught during review
- AI-introduced bugs (circular imports, bcrypt compatibility) fixed manually
- Final architectural decisions were my own

---

*Appendix for COMP3011 CW1 submission*
