"""
Spring Boot to FastAPI Framework Mappings (spec section 27).
"""

SPRING_TO_FASTAPI_ANNOTATIONS = {
    "RestController": "",
    "Controller": "",
    "RequestMapping": "APIRouter(prefix='{path}')",
    "GetMapping": "@router.get('{path}')",
    "PostMapping": "@router.post('{path}')",
    "PutMapping": "@router.put('{path}')",
    "DeleteMapping": "@router.delete('{path}')",
    "RequestBody": "body: {type}",
    "PathVariable": "{name}: {type}",
    "RequestParam": "{name}: {type} = Query(...)",
    "Autowired": "Depends(...)",
    "Service": "",
    "Repository": "",
}
