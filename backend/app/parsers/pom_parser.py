"""
Parses a Maven pom.xml into structured facts: Java version, dependencies,
and whether Spring Boot is in use (and which version).

Maven POMs declare a default XML namespace, which ElementTree requires you
to address explicitly -- we strip it up front so tag lookups stay simple.
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def _strip_namespace(root: ET.Element) -> None:
    for el in root.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]


def parse_pom(pom_path: Path) -> dict:
    result = {
        "java_version": None,
        "dependencies": [],  # [{"name": "group:artifact", "version": "..."}]
        "framework": None,   # "spring-boot" or None
        "framework_version": None,
    }
    try:
        tree = ET.parse(pom_path)
    except ET.ParseError:
        return result
    root = tree.getroot()
    _strip_namespace(root)

    # Java version: <properties><maven.compiler.source>17</...> or java.version
    props = root.find("properties")
    if props is not None:
        for tag in ("maven.compiler.source", "maven.compiler.release", "java.version"):
            el = props.find(tag)
            if el is not None and el.text:
                result["java_version"] = el.text.strip()
                break

    # Spring Boot via parent artifact
    parent = root.find("parent")
    if parent is not None:
        artifact = parent.findtext("artifactId", "")
        if "spring-boot-starter-parent" in artifact:
            result["framework"] = "spring-boot"
            result["framework_version"] = parent.findtext("version")

    # Dependencies
    deps_el = root.find("dependencies")
    if deps_el is not None:
        for dep in deps_el.findall("dependency"):
            group = dep.findtext("groupId", "")
            artifact = dep.findtext("artifactId", "")
            version = dep.findtext("version")
            name = f"{group}:{artifact}" if group else artifact
            result["dependencies"].append({"name": name, "group_id": group, "artifact_id": artifact, "version": version})
            if result["framework"] is None and "spring-boot-starter" in artifact:
                result["framework"] = "spring-boot"

    return result
