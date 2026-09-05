# Architecture

Java Source -> JavaParser (subprocess) -> Java AST (JSON)
            -> IR Builder -> Universal IR (Pydantic models)
            -> Migration Rule Engine (deterministic, per target)
            -> AI Translation Agent (fills gaps rules can't cover)
            -> Target Generator (Python/TS/Kotlin) -> Target Project
            -> Docker Build/Test -> Error Analyzer -> Repair Agent -> retry (max N)
            -> Validation Agent -> Report

See project chat log / README for full rationale. Filled in incrementally per phase.
