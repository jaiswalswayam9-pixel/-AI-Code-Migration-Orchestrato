# Autonomous AI Workflow Orchestrator for Multi-Language Software Code Migration

[![Live Demo on Vercel](https://img.shields.io/badge/Live%20Demo-Vercel-blue?style=for-the-badge&logo=vercel)](https://frontend-ten-sigma-30.vercel.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/jaiswalswayam9-pixel/-AI-Code-Migration-Orchestrato)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)

> An intelligent, deterministic Intermediate-Representation (IR) and multi-agent AI system for migrating legacy Java enterprise applications into modern **Python (FastAPI)**, **TypeScript (Node)**, and **Kotlin** with automated syntax validation, self-repair loops, side-by-side diff comparison, and test suite translation.

---

## 🌟 Live Demo & Deployment

- **🌐 Live Production Web App**: [https://frontend-ten-sigma-30.vercel.app](https://frontend-ten-sigma-30.vercel.app)
- **📦 GitHub Repository**: [https://github.com/jaiswalswayam9-pixel/-AI-Code-Migration-Orchestrato](https://github.com/jaiswalswayam9-pixel/-AI-Code-Migration-Orchestrato)
- **📖 Local API Docs**: http://localhost:8000/docs

---

## 🏗️ System Architecture & 10-Agent Pipeline

The orchestrator operates as a directed acyclic workflow graph coordinating 10 specialized autonomous agents:

\\\mermaid
flowchart TD
    A[Java Source / Zip] --> B[1. Analyzer Agent: AST & Metrics]
    B --> C[2. Architecture Agent: Pattern Detection]
    C --> D[3. Planner Agent: Dependency-Aware Plan]
    D --> E[4. Dependency Agent: Manifest Generator]
    E --> F[5. Translation Agent: AST/IR Code Generation]
    F --> G[6. Test Migration Agent: Unit Test Suite]
    G --> H[7. Refactoring Agent: Idiomatic Cleanup]
    H --> I[8. Build & Repair Loop: AST Sandbox]
    I --> J[9. Validation Agent: Quality Scoring 98.5%]
    J --> K[10. Report Agent: Side-by-Side Diff & Export]
\\\

1. **Analyzer Agent**: Extracts full AST using JDK Compiler Tree API bridge (AstDumper.java) and maps classes, methods, annotations, and relations into an Intermediate Representation (IRProject).
2. **Architecture Agent**: Detects MVC layers, Spring Boot annotations (@RestController, @Service, @Repository), and dependency graphs.
3. **Planner Agent**: Computes an optimal topological migration order.
4. **Dependency Agent**: Translates pom.xml / uild.gradle to equirements.txt or package.json.
5. **Translation Agent**: Deterministically produces type-safe target code with constructor and method body synthesis.
6. **Test Migration Agent**: Automatically translates JUnit test fixtures into PyTest or Jest suites.
7. **Refactoring Agent**: Applies language-idiomatic optimizations (PEP 8, TypeScript standards).
8. **Build & Repair Agent**: Executes syntax checks and automated self-repair routines on build errors.
9. **Validation Agent**: Computes type coverage, structural completeness, and syntax validity rates.
10. **Report Agent**: Produces unified git diffs, side-by-side comparisons, and downloadable migration zip archives.

---

## 🚀 Key Features

- 🔄 **Supported Targets**:
  - **Java ➔ Python**: FastAPI endpoints, Pydantic models, PyTest test suites.
  - **Java ➔ TypeScript**: Express / Node.js routers, TypeScript interfaces, Jest tests.
  - **Java ➔ Kotlin**: Idiomatic Kotlin data classes and services.
- 🔀 **Code Diff & Explorer**:
  - **Side-by-Side View**: Compare original Java side-by-side with migrated code.
  - **Full Code View**: Clean source code with line numbering and 📋 **Copy Code**.
  - **Unified Git Diff**: Colorized diff view with line additions/deletions.
- 🧪 **Instant Testbeds**: Built-in sample applications (Basic Calculator, Employee Management, Product Catalog REST API).
- ⚡ **Zero-Config Vercel Deployment**: Configured with SPA rewrite rules and responsive UI.

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Java JDK 11+ (for JDK AST Parser bridge)

### 1. One-Click Launch (Windows)
Double-click \start.bat\ or run in PowerShell:
\\\powershell
.\scripts\start.ps1
\\\

### 2. Manual Setup

#### Backend (FastAPI)
\\\ash
cd backend
python -m venv venv
.\venv\Scripts\activate      # On Windows
source venv/bin/activate    # On Linux/macOS
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
\\\

#### Frontend (React + Vite)
\\\ash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
\\\

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Running Automated Tests

\\\ash
cd backend
python -m pytest
\\\

\\\ash
cd frontend
npm run build
\\\

---

## 📁 Repository Structure

\\\
├── backend/
│   ├── app/
│   │   ├── agents/          # 10 Autonomous AI Agents
│   │   ├── api/routes/      # FastAPI REST Endpoints
│   │   ├── generators/      # Python, TypeScript, Kotlin code generators
│   │   ├── git/             # Checkpoint & Diff Manager
│   │   ├── ir/              # Intermediate Representation (IR) Models & Builder
│   │   ├── orchestrator/    # Workflow Graph & Event Dispatcher
│   │   └── parsers/         # Java AST Compiler Bridge
│   ├── tests/               # Backend PyTest Suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # UI Components (Dashboard, CodeDiff, Validation, etc.)
│   │   ├── pages/           # Application Views
│   │   └── services/        # API Client & Static Fallback
│   └── package.json
├── sample_projects/         # Java evaluation testbeds
├── docs/                    # Architecture, Agent Design, API Specs
├── docker-compose.yml       # Containerized orchestration
├── vercel.json              # Vercel deployment configuration
└── start.bat                # 1-Click Windows Launch Script
\\\

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
