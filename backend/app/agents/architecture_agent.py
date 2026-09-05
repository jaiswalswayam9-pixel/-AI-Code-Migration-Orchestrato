"""
Architecture Analyzer Agent (spec section 3).

Analyzes project architecture, layers, component responsibilities,
and framework mappings (e.g., Spring Boot MVC -> FastAPI / Express / Ktor).
"""
from typing import Any
from app.ir.models import IRProject, IRClass


def analyze_architecture(ir: IRProject, project_analysis: dict | None = None) -> dict[str, Any]:
    """
    Examines project structure and classes to detect architectural patterns,
    component roles (models, repositories, services, controllers, utilities),
    and target framework scaffolding recommendations.
    """
    layers: dict[str, list[str]] = {
        "models": [],
        "repositories": [],
        "services": [],
        "controllers": [],
        "utilities": [],
        "configs": [],
    }

    component_graph: list[dict[str, Any]] = []

    for cu in ir.compilation_units:
        for t in cu.types:
            name = t.name
            ann_names = [a.name for a in t.annotations]
            field_types = [f.type.name for f in t.fields]

            # Detect role based on annotations, name suffix, or extends
            if any(a in ann_names for a in ["RestController", "Controller"]) or name.endswith("Controller") or name.endswith("Resource"):
                role = "controllers"
            elif any(a in ann_names for a in ["Service"]) or name.endswith("Service") or name.endswith("Manager"):
                role = "services"
            elif any(a in ann_names for a in ["Repository"]) or name.endswith("Repository") or name.endswith("Dao"):
                role = "repositories"
            elif any(a in ann_names for a in ["Entity", "Table"]) or name.endswith("Entity") or name.endswith("DTO") or name.endswith("Model"):
                role = "models"
            elif any(a in ann_names for a in ["Configuration", "Component"]) or name.endswith("Config"):
                role = "configs"
            elif t.kind == "enum":
                role = "models"
            elif not t.methods and t.fields:
                role = "models"
            else:
                role = "utilities"

            layers[role].append(name)

            component_graph.append({
                "name": name,
                "kind": t.kind,
                "role": role[:-1] if role.endswith("s") else role,
                "package": cu.package,
                "dependencies": [ft for ft in field_types if ft != name],
                "methods_count": len(t.methods),
                "fields_count": len(t.fields),
            })

    framework = (project_analysis or {}).get("framework") or "Spring Boot" if (layers["controllers"] or layers["services"]) else "Standard Java"

    architecture_type = "Layered MVC Architecture" if (layers["controllers"] and layers["services"]) else "Modular Java Library"

    return {
        "architecture_type": architecture_type,
        "source_framework": framework,
        "layers": layers,
        "component_graph": component_graph,
        "recommendations": {
            "python": "FastAPI + Pydantic + SQLAlchemy (Async/Sync Repository pattern)" if framework.startswith("Spring") else "Standard Python Package",
            "typescript": "Express / NestJS + Prisma / TypeORM" if framework.startswith("Spring") else "TypeScript Node / ESM Library",
            "kotlin": "Ktor / Spring Boot Kotlin + Exposed" if framework.startswith("Spring") else "Kotlin JVM Multiplatform Library",
        }
    }
