# Java AST Bridge

Parses Java source into a JSON AST using the JDK's own built-in Compiler
Tree API (`com.sun.source.tree` / `com.sun.source.util`), which ships
with every JDK -- no external dependency (JavaParser, Maven Central, etc.)
required.

## Why not JavaParser?

This project was built in a network-sandboxed environment where Maven
Central was not reachable and JavaParser does not publish plain jars as
GitHub release assets. Rather than fake it, we used the JDK's own
compiler frontend instead -- which is arguably even more authoritative
("this is literally what javac itself parses Java with"), and has the
practical benefit of zero external dependencies for anyone building this
project, on any machine, regardless of network policy.

If you have full internet access and prefer JavaParser (e.g. for its
symbol-resolution features, which this bridge does not attempt), it's a
drop-in swap: same JSON contract, different implementation of
`AstDumper.java`.

## Build

    javac -d bin src/AstDumper.java

(`app/parsers/java_parser.py` does this automatically on first use.)

## Run

    java -cp bin AstDumper File1.java File2.java ...

Outputs one JSON object per line, one per input file.

## Scope

This performs parsing only (`task.parse()`), not full semantic analysis
(`task.analyze()`) -- so types appear as their source-text form (e.g.
`"List<Employee>"`), not resolved/bound types. That's what the
Intermediate Representation (Phase 7) expects: a structural model, not a
type-checker.

Note: for `INTERFACE` types, `extends` clauses appear in the JSON
`implements` list, not `extends` -- this mirrors `com.sun.source.tree`'s
own behavior (interfaces can extend multiple interfaces, so javac puts
them all in `getImplementsClause()`; `getExtendsClause()` is
class-only and always null for interfaces).
