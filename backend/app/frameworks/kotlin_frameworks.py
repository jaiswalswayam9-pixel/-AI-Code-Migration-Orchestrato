"""
Kotlin Framework Mappings (Ktor / Spring Boot Kotlin).
"""

SPRING_TO_KTOR_ANNOTATIONS = {
    "RestController": "",
    "GetMapping": "get('{path}') {{ ... }}",
    "PostMapping": "post('{path}') {{ ... }}",
}
