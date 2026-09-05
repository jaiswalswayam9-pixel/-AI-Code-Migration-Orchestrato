"""
Node / Express Framework Mappings.
"""

SPRING_TO_EXPRESS_ANNOTATIONS = {
    "RestController": "",
    "Controller": "",
    "GetMapping": "router.get('{path}', ...)",
    "PostMapping": "router.post('{path}', ...)",
    "PutMapping": "router.put('{path}', ...)",
    "DeleteMapping": "router.delete('{path}', ...)",
}
