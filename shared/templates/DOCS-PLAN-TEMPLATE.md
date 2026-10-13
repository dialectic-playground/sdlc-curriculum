# Documentation Plan — {{TITLE}}

| Field | Value |
| :-- | :-- |
| Project | `{{SLUG}}` |
| Tools | {{TOOLS}} |
| Author | *your name* |
| Version / date | *0.1 — YYYY-MM-DD* |

> **Purpose of this document.** This plan says which documentation will exist for the
> project, who it is for, where it lives, how it stays accurate, and when it is done. The
> curriculum *supplies* the user-facing documents (`specs/user-manual.md`, help text). You own
> the engineering documentation (HLD, LLD, RTM, MTP, code docs, changelog).

## 1. Audiences

| Audience | Needs | Primary documents |
| :-- | :-- | :-- |
| End users | *how to run the tool, options, examples, exit status* | `specs/user-manual.md`, `--help` |
| Maintainers | *architecture, rationale, how to build/test/release* | HLD, LLD, README, CHANGELOG |
| Reviewers / graders | *evidence that requirements are met* | RTM, MTP, CI results |

## 2. Document inventory

| Document | Location | Owner | Format / standard | Status |
| :-- | :-- | :-- | :-- | :-- |
| User manual | `specs/user-manual.md` | curriculum | Markdown (man-page structure) | Supplied |
| Help / version text | built into the tool | you | must match the user manual exactly (CONV-23) | |
| High-Level Design | `assignment/hld.md` | you | `shared/templates/HLD-TEMPLATE.md` | |
| Low-Level Design | `assignment/lld.md` | you | `shared/templates/LLD-TEMPLATE.md` | |
| Traceability matrix | `assignment/rtm.md` | you | `shared/templates/RTM-TEMPLATE.md` | |
| Master test plan | `assignment/master-test-plan.md` | you | `shared/templates/MASTER-TEST-PLAN-TEMPLATE.md` | |
| API / code documentation | source files | you | *docstrings / rustdoc / godoc* | |
| Changelog | `assignment/CHANGELOG.md` | you | Keep a Changelog 1.1 | |

## 3. Code documentation standard

*Choose and describe the standard for each language you use, for example PEP 257 docstrings
with type hints, `///` rustdoc on every `pub` item, or Go doc comments on every exported
identifier. State the rule: every public function and type is documented (Principle 7), and
comments explain why, not what (Principle 2).*

## 4. Change records

*Explain how significant changes are recorded (Principle 17): commit-message convention (e.g.
Conventional Commits), CHANGELOG entries for each release, and ADR updates in the HLD.*

## 5. Review and maintenance

| Trigger | Documents to update | Reviewer |
| :-- | :-- | :-- |
| *A requirement interpretation changes* | *HLD, LLD, RTM* | |
| *A new defect is fixed* | *MTP §4.2, RTM, CHANGELOG* | |

## 6. Definition of done for documentation

- [ ] Every template prompt is replaced; no *italic prompts* remain.
- [ ] Help output matches `specs/user-manual.md` byte-for-byte (public test passes).
- [ ] Every RTM row is `Verified` or has a justified gap.
- [ ] Every public API item has documentation, and the language's doc tool runs cleanly.
- [ ] The CHANGELOG has an entry for the submitted version.
