"""
Shared naming helpers + a project-wide class registry.

The registry matters because generated files need to import each other
correctly: EmployeeController references EmployeeService, which needs to
become `from .employee_service import EmployeeService` in the generated
Python file. Building this registry once, up front, from the whole
IRProject, is what makes that possible -- generating one file in
isolation can\'t know where a referenced class will end up.
"""
import re
from app.ir.models import IRProject

_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(name: str) -> str:
    return _CAMEL_BOUNDARY.sub("_", name).lower()


def to_kebab_case(name: str) -> str:
    return _CAMEL_BOUNDARY.sub("-", name).lower()


def package_to_path(package: str | None) -> str:
    return package.replace(".", "/") if package else ""


class ProjectRegistry:
    """Maps a Java simple class name -> its module\'s dotted import path
    in the generated project, e.g. "EmployeeService" -> "employee_management.employee_service"."""

    def __init__(self, ir: IRProject, root_package_name: str):
        self.root_package_name = root_package_name
        self._class_to_module: dict[str, str] = {}

        for cu in ir.compilation_units:
            if cu.parse_error:
                continue
            for t in cu.types:
                module_name = to_snake_case(t.name)
                pkg_path = package_to_path(cu.package)
                dotted = f"{root_package_name}.{pkg_path.replace('/', '.')}.{module_name}" if pkg_path else f"{root_package_name}.{module_name}"
                self._class_to_module[t.name] = dotted.replace("..", ".")

    def module_for(self, class_name: str) -> str | None:
        return self._class_to_module.get(class_name)

    def is_project_local(self, class_name: str) -> bool:
        return class_name in self._class_to_module


class TypeScriptProjectRegistry:
    """TS/ESM imports are relative ('./employee', '../foo/bar'), unlike
    Python's absolute dotted imports -- so this needs each class's
    directory + file stem, and a relative-path computation between two
    generated files, rather than one fixed dotted path per class."""

    def __init__(self, ir: IRProject):
        self._dir: dict[str, str] = {}    # class name -> package-relative dir, e.g. "com/example/employees"
        self._stem: dict[str, str] = {}   # class name -> kebab-case file stem

        for cu in ir.compilation_units:
            if cu.parse_error:
                continue
            pkg_path = package_to_path(cu.package)
            for t in cu.types:
                self._dir[t.name] = pkg_path
                self._stem[t.name] = to_kebab_case(t.name)

    def is_project_local(self, class_name: str) -> bool:
        return class_name in self._dir

    def import_path_from(self, from_pkg_path: str, class_name: str) -> str:
        """Relative ESM import path from a file in from_pkg_path to class_name's file."""
        import os
        target_dir = self._dir[class_name]
        stem = self._stem[class_name]
        rel_dir = os.path.relpath(target_dir or ".", from_pkg_path or ".")
        if rel_dir == ".":
            return f"./{stem}"
        rel_dir = rel_dir.replace(os.sep, "/")
        prefix = "" if rel_dir.startswith("..") else "./"
        return f"{prefix}{rel_dir}/{stem}"


class KotlinProjectRegistry:
    """Kotlin declares an actual `package` statement per file (unlike TS),
    so same-package references need NO import at all -- only
    cross-package references do, as a fully-dotted `package.ClassName`."""

    def __init__(self, ir: IRProject):
        self._package: dict[str, str] = {}  # class name -> dotted Java/Kotlin package
        for cu in ir.compilation_units:
            if cu.parse_error:
                continue
            for t in cu.types:
                self._package[t.name] = cu.package or ""

    def is_project_local(self, class_name: str) -> bool:
        return class_name in self._package

    def import_for(self, from_package: str, class_name: str) -> str | None:
        target_package = self._package[class_name]
        if target_package == from_package:
            return None
        return f"{target_package}.{class_name}" if target_package else class_name
