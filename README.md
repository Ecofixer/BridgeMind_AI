# BridgeMind AI

**Agentic AI + BIM Smart Bridge Design System**  
For the **Zengwen River Landscape Bridge** competition (曾文溪景觀橋競賽)

---

## Project Goal

BridgeMind AI is not just a report generator. It is a **usable prototype system** that can:

1. Read bridge-related project data
2. Analyze engineering feasibility
3. Analyze environmental and sustainability issues
4. Generate bridge design concepts
5. Generate BIM component lists and modeling parameters
6. Explain how AI technologies (RAG, CNN, PINN, Agentic AI) can be applied
7. Estimate cost and schedule
8. Generate final reports and presentation outlines

---

## System Architecture

```
Bridge Project Manager Agent (00)
│
├── 1. Research Agent (01)
│   └── Collects EIA, feasibility reports, bridge cases, regulations
│
├── 2. Engineering Analysis Agent (02)
│   └── Route, geotechnical, structural, drainage, flood control, construction feasibility
│
├── 3. Environmental & Sustainability Agent (03)
│   └── Wetlands, ecology, water quality, noise, air pollution, landscape, SDGs
│
├── 4. Design, BIM & Visualization Agent (04)
│   └── Bridge type, exterior design, landmark concept, BIM list, parameters, AI image prompts
│
├── 5. AI Integration Agent (05)
│   └── RAG, CNN, PINN, Digital Twin, Generative AI, Agentic AI per design stage
│
├── 6. Cost & Schedule Agent (06)
│   └── Engineering cost, schedule, maintenance, lifecycle, traditional vs AI workflow
│
└── 7. Report Agent (07)
    └── Final report, PPT outline, conclusions, scoring alignment
```

---

## 7-Agent Overview

| ID | Agent | Role | Output File |
|----|-------|------|-------------|
| 00 | Bridge Project Manager | Chief engineer / PM; coordinates workflow, checks consistency, competition strategy | `outputs/project_manager_summary.md` |
| 01 | Research | Document collection, summarization, knowledge organization | `outputs/research_summary.md` |
| 02 | Engineering Analysis | Core civil engineering feasibility analysis | `outputs/engineering_analysis.md` |
| 03 | Environmental & Sustainability | Ecological impact, mitigation, SDGs alignment | `outputs/environmental_sustainability.md` |
| 04 | Design, BIM & Visualization | Bridge design concept, BIM parameters, visualization | `outputs/design_bim_visualization.md`, `outputs/bim_parameters.json` |
| 05 | AI Integration | AI strategy across all project stages | `outputs/ai_integration_plan.md` |
| 06 | Cost & Schedule | Cost estimation, schedule, lifecycle, AI efficiency | `outputs/cost_schedule_analysis.md` |
| 07 | Report | Final report, PPT outline, scoring alignment | `outputs/final_report.md`, `outputs/ppt_outline.md` |

---

## Data Flow

```
data/bridge_inputs/zengwen_bridge_profile.json
        │
        ▼
data/raw_documents/  ──→  01 Research Agent  ──→  outputs/research_summary.md
  ├── environmental_reports/
  ├── feasibility_reports/
  ├── bridge_cases/
  └── regulations/
        │
        ▼
data/knowledge_base/zengwen_bridge_notes.md
        │
        ├──────────────────────────────────────────────────────────┐
        ▼                          ▼                             ▼
02 Engineering Analysis    03 Environmental & Sustainability      │
        │                          │                             │
        └──────────┬───────────────┘                             │
                   ▼                                             │
        04 Design, BIM & Visualization                           │
                   │                                             │
        ┌──────────┴──────────┐                                  │
        ▼                     ▼                                  │
05 AI Integration    06 Cost & Schedule                         │
        │                     │                                  │
        └──────────┬──────────┘                                  │
                   ▼                                             │
        00 Project Manager  ◄──────────────────────────────────┘
                   │
                   ▼
        07 Report Agent
                   │
                   ▼
        outputs/final_report.md
        outputs/ppt_outline.md
```

---

## Project Structure

```
BridgeMind_AI/
├── app.py                          # CLI entry point (to be implemented)
├── README.md
├── requirements.txt
├── config/
│   ├── settings.py
│   └── agent_config.py
├── data/
│   ├── raw_documents/
│   │   ├── environmental_reports/  # EIA reports
│   │   ├── feasibility_reports/    # Feasibility studies
│   │   ├── bridge_cases/           # Reference bridge projects
│   │   └── regulations/            # Codes and standards
│   ├── processed_text/             # Extracted PDF text (RAG)
│   ├── bridge_inputs/
│   │   └── zengwen_bridge_profile.json
│   └── knowledge_base/
│       └── zengwen_bridge_notes.md
├── agents/
│   ├── 00_project_manager_agent.py
│   ├── 01_research_agent.py
│   ├── 02_engineering_analysis_agent.py
│   ├── 03_environmental_sustainability_agent.py
│   ├── 04_design_bim_visualization_agent.py
│   ├── 05_ai_integration_agent.py
│   ├── 06_cost_schedule_agent.py
│   └── 07_report_agent.py
├── prompts/
│   ├── 00_project_manager_prompt.md
│   ├── 01_research_prompt.md
│   ├── 02_engineering_analysis_prompt.md
│   ├── 03_environmental_sustainability_prompt.md
│   ├── 04_design_bim_visualization_prompt.md
│   ├── 05_ai_integration_prompt.md
│   ├── 06_cost_schedule_prompt.md
│   └── 07_report_prompt.md
├── rag/
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── vector_store.py
│   └── retriever.py
├── outputs/
│   ├── project_manager_summary.md
│   ├── research_summary.md
│   ├── engineering_analysis.md
│   ├── environmental_sustainability.md
│   ├── design_bim_visualization.md
│   ├── ai_integration_plan.md
│   ├── cost_schedule_analysis.md
│   ├── final_report.md
│   ├── ppt_outline.md
│   └── bim_parameters.json
├── exports/
│   ├── word/
│   ├── ppt/
│   ├── images/
│   └── bim/
└── utils/
    ├── llm_client.py
    ├── file_utils.py
    ├── json_utils.py
    ├── markdown_utils.py
    └── report_exporter.py
```

---

## Expected Outputs

| File | Producer | Description |
|------|----------|-------------|
| `project_manager_summary.md` | Agent 00 | Workflow summary, task assignment, integrated decision, competition strategy |
| `research_summary.md` | Agent 01 | Document summaries, key data, references, missing-data checklist |
| `engineering_analysis.md` | Agent 02 | Route, geotechnical, structural, drainage, construction feasibility |
| `environmental_sustainability.md` | Agent 03 | Environmental risk matrix, mitigation, SDGs alignment |
| `design_bim_visualization.md` | Agent 04 | Bridge type, exterior design, BIM list, AI image prompts |
| `bim_parameters.json` | Agent 04 | Structured BIM modeling parameters |
| `ai_integration_plan.md` | Agent 05 | AI application matrix, traditional vs AI comparison |
| `cost_schedule_analysis.md` | Agent 06 | Cost items, schedule, lifecycle, AI efficiency |
| `final_report.md` | Agent 07 | Integrated final technical report |
| `ppt_outline.md` | Agent 07 | 15-slide presentation outline |

---

## Key Zengwen River Bridge Data

| Parameter | Value |
|-----------|-------|
| River width | ~450–500 m |
| Design speed | 100 km/hr |
| Main bridge width | 33 m (two-way 4-lane) |
| Motorcycle lane | 3.0 m each side |
| Soil condition | Silty sand and sandy silt |
| Foundation | 1.5–2.0 m full-casing cast-in-place piles |
| Development area | 4.61 ha |
| Detention volume | 4,090 m³ |
| Environmental constraints | Wetland, black-faced spoonbill habitat, estuary ecology, water quality |

---

## Competition Support

BridgeMind AI addresses typical competition scoring categories:

- **Engineering feasibility** — Route, structure, geotechnical, drainage, construction (Agent 02)
- **Environmental sustainability** — Wetland, ecology, SDGs, mitigation (Agent 03)
- **Design innovation** — Landmark bridge concept, local identity, BIM (Agent 04)
- **AI innovation** — RAG, CNN, PINN, Agentic AI, Digital Twin (Agent 05)
- **Cost & schedule** — Lifecycle cost, AI-assisted efficiency (Agent 06)
- **Presentation quality** — Final report, PPT outline, scoring alignment (Agent 07)

---

## Status

Documentation and prompt files are complete. Agent logic, RAG pipeline, and CLI are **not yet implemented**.

## License

MIT
