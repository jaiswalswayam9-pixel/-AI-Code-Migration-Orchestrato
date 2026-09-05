"""
Parses build.gradle / build.gradle.kts via targeted regexes rather than a
full Groovy/Kotlin-DSL parser -- Gradle build files are executable scripts,
not declarative data, so a complete parse would mean embedding a Groovy
interpreter. This covers the common declarative patterns real projects use.
"""
import re
from pathlib import Path

_JAVA_VERSION_RE = re.compile(r"sourceCompatibility\s*=?\s*['\"]?(?:JavaVersion\.VERSION_)?(\d+(?:\.\d+)?)")
_DEPENDENCY_RE = re.compile(r"""(?:implementation|api|compile|testImplementation)\s*[\(]?['\"]([\w\.\-]+):([\w\.\-]+):?([\w\.\-]*)['\"]""")
_SPRING_BOOT_PLUGIN_RE = re.compile(r"""org\.springframework\.boot['\"]?\s*version\s*['\"]([\d\.]+)""")


def parse_gradle(build_file_path: Path) -> dict:
    result = {
        "java_version": None,
        "dependencies": [],
        "framework": None,
        "framework_version": None,
    }
    try:
        text = build_file_path.read_text(errors="ignore")
    except OSError:
        return result

    version_match = _JAVA_VERSION_RE.search(text)
    if version_match:
        result["java_version"] = version_match.group(1)

    for group, artifact, version in _DEPENDENCY_RE.findall(text):
        name = f"{group}:{artifact}"
        result["dependencies"].append({"name": name, "version": version or None})
        if "spring-boot-starter" in artifact:
            result["framework"] = "spring-boot"

    spring_match = _SPRING_BOOT_PLUGIN_RE.search(text)
    if spring_match:
        result["framework"] = "spring-boot"
        result["framework_version"] = spring_match.group(1)

    return result
