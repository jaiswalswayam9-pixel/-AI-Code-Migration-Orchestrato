"""
Dependency Mapping Agent (spec section 9).

Maps Maven/Gradle dependencies to target-language package managers:
- Python: requirements.txt / pyproject.toml
- TypeScript: package.json
- Kotlin: build.gradle.kts
"""
from typing import Any

DEPENDENCY_MAP: dict[str, dict[str, dict[str, str]]] = {
    "org.springframework.boot:spring-boot-starter-web": {
        "python": {"name": "fastapi>=0.115.0\nuvicorn>=0.30.0", "status": "automatic", "confidence": "high"},
        "typescript": {"name": "express: ^4.19.2", "status": "automatic", "confidence": "high"},
        "kotlin": {"name": "org.springframework.boot:spring-boot-starter-web", "status": "automatic", "confidence": "high"},
    },
    "org.springframework.boot:spring-boot-starter-data-jpa": {
        "python": {"name": "sqlalchemy>=2.0.0", "status": "automatic", "confidence": "high"},
        "typescript": {"name": "typeorm: ^0.3.20", "status": "automatic", "confidence": "high"},
        "kotlin": {"name": "org.springframework.boot:spring-boot-starter-data-jpa", "status": "automatic", "confidence": "high"},
    },
    "org.springframework.boot:spring-boot-starter-test": {
        "python": {"name": "pytest>=8.0.0\npytest-asyncio>=0.23.0", "status": "automatic", "confidence": "high"},
        "typescript": {"name": "vitest: ^2.0.0\nsupertest: ^7.0.0", "status": "automatic", "confidence": "high"},
        "kotlin": {"name": "org.springframework.boot:spring-boot-starter-test", "status": "automatic", "confidence": "high"},
    },
    "org.projectlombok:lombok": {
        "python": {"name": "pydantic>=2.8.0", "status": "automatic", "confidence": "high"},
        "typescript": {"name": "# handled natively via TypeScript classes/types", "status": "automatic", "confidence": "high"},
        "kotlin": {"name": "# handled natively via Kotlin data classes", "status": "automatic", "confidence": "high"},
    },
    "com.fasterxml.jackson.core:jackson-databind": {
        "python": {"name": "pydantic>=2.8.0", "status": "automatic", "confidence": "high"},
        "typescript": {"name": "# native JSON support", "status": "automatic", "confidence": "high"},
        "kotlin": {"name": "com.fasterxml.jackson.module:jackson-module-kotlin", "status": "automatic", "confidence": "high"},
    },
    "org.junit.jupiter:junit-jupiter-api": {
        "python": {"name": "pytest>=8.0.0", "status": "automatic", "confidence": "high"},
        "typescript": {"name": "vitest: ^2.0.0", "status": "automatic", "confidence": "high"},
        "kotlin": {"name": "org.junit.jupiter:junit-jupiter-api", "status": "automatic", "confidence": "high"},
    },
}


def map_dependencies(source_dependencies: list[dict[str, Any]], target_language: str) -> list[dict[str, Any]]:
    """
    Translates a list of Maven/Gradle dependencies to target packages.
    """
    mapped: list[dict[str, Any]] = []

    for dep in source_dependencies:
        group_id = dep.get("group_id", "")
        artifact_id = dep.get("artifact_id", "")
        key = f"{group_id}:{artifact_id}"

        mapping_info = DEPENDENCY_MAP.get(key, {}).get(target_language)
        if mapping_info:
            mapped.append({
                "source_dependency": key,
                "version": dep.get("version"),
                "target_equivalent": mapping_info["name"],
                "status": mapping_info["status"],
                "confidence": mapping_info["confidence"],
            })
        else:
            # Fallback heuristic
            mapped.append({
                "source_dependency": key if key != ":" else dep.get("name", "unknown"),
                "version": dep.get("version"),
                "target_equivalent": f"# TODO: find target equivalent for {key}",
                "status": "requires_human_review",
                "confidence": "low",
            })

    return mapped


def generate_manifest_content(mapped_dependencies: list[dict[str, Any]], target_language: str, project_name: str) -> tuple[str, str]:
    """
    Returns (manifest_filename, manifest_content)
    """
    if target_language == "python":
        lines = [
            f"# Requirements for {project_name}",
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.30.0",
            "pydantic>=2.8.0",
            "pytest>=8.0.0",
        ]
        for m in mapped_dependencies:
            eq = m.get("target_equivalent", "")
            if eq and not eq.startswith("#") and eq not in lines:
                lines.append(eq)
        return "requirements.txt", "\n".join(lines) + "\n"

    elif target_language == "typescript":
        deps = {
            "express": "^4.19.2",
            "cors": "^2.8.5",
        }
        dev_deps = {
            "typescript": "^5.5.4",
            "@types/node": "^22.0.0",
            "@types/express": "^4.17.21",
            "vitest": "^2.0.5",
        }
        import json
        pkg = {
            "name": project_name.lower().replace("_", "-"),
            "version": "1.0.0",
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "test": "vitest run"
            },
            "dependencies": deps,
            "devDependencies": dev_deps
        }
        return "package.json", json.dumps(pkg, indent=2) + "\n"

    elif target_language == "kotlin":
        content = f"""plugins {{
    kotlin("jvm") version "2.0.0"
    application
}}

repositories {{
    mavenCentral()
}}

dependencies {{
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
}}

tasks.test {{
    useJUnitPlatform()
}}
"""
        return "build.gradle.kts", content

    return "README_DEPS.txt", "# Target dependencies\n"
