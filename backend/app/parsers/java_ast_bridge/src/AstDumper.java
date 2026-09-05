import javax.tools.*;
import com.sun.source.tree.*;
import com.sun.source.util.*;
import java.io.*;
import java.util.*;

/**
 * Parses one or more Java source files into a language-neutral JSON AST,
 * using ONLY the JDK's own public, exported Compiler Tree API
 * (com.sun.source.tree / com.sun.source.util). No external library is
 * required.
 *
 * Captures structural class metadata, method signatures, AND method bodies
 * (statements, expressions, conditions, loops, calls, assignments, returns).
 *
 * Usage: java AstDumper <file1.java> [file2.java ...]
 * Output: one JSON object per input file, newline-delimited, to stdout.
 */
public class AstDumper {

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("Usage: java AstDumper <file1.java> [file2.java ...]");
            System.exit(1);
        }

        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        StandardJavaFileManager fm = compiler.getStandardFileManager(null, null, null);

        for (String path : args) {
            File file = new File(path);
            Map<String, Object> result = new LinkedHashMap<>();
            DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
            try {
                if (!file.exists()) {
                    result.put("file", path);
                    result.put("error", "File not found: " + path);
                    System.out.println(Json.stringify(result));
                    continue;
                }

                Iterable<? extends JavaFileObject> units = fm.getJavaFileObjects(file);
                JavacTask task = (JavacTask) compiler.getTask(null, fm, diagnostics, null, null, units);
                Iterable<? extends CompilationUnitTree> trees = task.parse();

                CompilationUnitTree cu = trees.iterator().next();
                result.put("file", path);
                result.put("package", cu.getPackageName() != null ? cu.getPackageName().toString() : null);

                List<Object> imports = new ArrayList<>();
                for (ImportTree imp : cu.getImports()) {
                    Map<String, Object> importEntry = new LinkedHashMap<>();
                    importEntry.put("path", imp.getQualifiedIdentifier().toString());
                    importEntry.put("is_static", imp.isStatic());
                    imports.add(importEntry);
                }
                result.put("imports", imports);

                List<Object> types = new ArrayList<>();
                for (Tree t : cu.getTypeDecls()) {
                    if (t instanceof ClassTree) {
                        types.add(dumpType((ClassTree) t));
                    }
                }
                result.put("types", types);

                List<String> diagMessages = new ArrayList<>();
                boolean hasError = false;
                for (Diagnostic<? extends JavaFileObject> d : diagnostics.getDiagnostics()) {
                    if (d.getKind() == Diagnostic.Kind.ERROR) hasError = true;
                    diagMessages.add(d.getKind() + " line " + d.getLineNumber() + ": " + d.getMessage(null));
                }
                result.put("diagnostics", diagMessages);
                result.put("error", hasError ? "Source has syntax errors -- AST may be partial/unreliable, see diagnostics" : null);

            } catch (Exception e) {
                result.clear();
                result.put("file", path);
                result.put("error", e.getClass().getSimpleName() + ": " + e.getMessage());
            }
            System.out.println(Json.stringify(result));
        }
    }

    private static Map<String, Object> dumpType(ClassTree ct) {
        Map<String, Object> out = new LinkedHashMap<>();
        String kind;
        switch (ct.getKind()) {
            case INTERFACE: kind = "interface"; break;
            case ENUM: kind = "enum"; break;
            case ANNOTATION_TYPE: kind = "annotation"; break;
            case RECORD: kind = "record"; break;
            default: kind = "class";
        }
        out.put("kind", kind);
        out.put("name", ct.getSimpleName().toString());
        out.put("modifiers", modifiersOf(ct.getModifiers()));
        out.put("annotations", annotationsOf(ct.getModifiers()));
        out.put("extends", ct.getExtendsClause() != null ? ct.getExtendsClause().toString() : null);

        List<String> implementsList = new ArrayList<>();
        for (Tree impl : ct.getImplementsClause()) {
            implementsList.add(impl.toString());
        }
        out.put("implements", implementsList);

        List<Object> fields = new ArrayList<>();
        List<Object> constructors = new ArrayList<>();
        List<Object> methods = new ArrayList<>();
        List<Object> nestedTypes = new ArrayList<>();

        for (Tree member : ct.getMembers()) {
            if (member instanceof VariableTree) {
                fields.add(dumpField((VariableTree) member));
            } else if (member instanceof MethodTree) {
                MethodTree mt = (MethodTree) member;
                if (mt.getName().toString().equals("<init>")) {
                    constructors.add(dumpMethod(mt, true));
                } else {
                    methods.add(dumpMethod(mt, false));
                }
            } else if (member instanceof ClassTree) {
                nestedTypes.add(dumpType((ClassTree) member));
            }
        }

        out.put("fields", fields);
        out.put("constructors", constructors);
        out.put("methods", methods);
        out.put("nested_types", nestedTypes);
        return out;
    }

    private static Map<String, Object> dumpField(VariableTree vt) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("name", vt.getName().toString());
        out.put("type", vt.getType().toString());
        out.put("modifiers", modifiersOf(vt.getModifiers()));
        out.put("annotations", annotationsOf(vt.getModifiers()));
        if (vt.getInitializer() != null) {
            out.put("initializer", dumpExpression(vt.getInitializer()));
        } else {
            out.put("initializer", null);
        }
        return out;
    }

    private static Map<String, Object> dumpMethod(MethodTree mt, boolean isConstructor) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("name", isConstructor ? "<init>" : mt.getName().toString());
        out.put("return_type", mt.getReturnType() != null ? mt.getReturnType().toString() : null);
        out.put("modifiers", modifiersOf(mt.getModifiers()));
        out.put("annotations", annotationsOf(mt.getModifiers()));

        List<Object> params = new ArrayList<>();
        for (VariableTree p : mt.getParameters()) {
            Map<String, Object> param = new LinkedHashMap<>();
            param.put("name", p.getName().toString());
            param.put("type", p.getType().toString());
            params.add(param);
        }
        out.put("parameters", params);

        List<String> throwsList = new ArrayList<>();
        for (ExpressionTree ex : mt.getThrows()) {
            throwsList.add(ex.toString());
        }
        out.put("throws", throwsList);

        if (mt.getBody() != null) {
            out.put("body", dumpMethodBody(mt.getBody()));
        } else {
            out.put("body", null);
        }

        return out;
    }

    private static Map<String, Object> dumpMethodBody(BlockTree block) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("source_code", block.toString());
        List<Object> statements = new ArrayList<>();
        for (StatementTree st : block.getStatements()) {
            statements.add(dumpStatement(st));
        }
        out.put("statements", statements);
        return out;
    }

    private static Map<String, Object> dumpStatement(StatementTree st) {
        if (st == null) return null;
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("source", st.toString());

        if (st instanceof VariableTree) {
            VariableTree vt = (VariableTree) st;
            out.put("kind", "variable_decl");
            out.put("name", vt.getName().toString());
            out.put("type", vt.getType().toString());
            out.put("modifiers", modifiersOf(vt.getModifiers()));
            out.put("initializer", vt.getInitializer() != null ? dumpExpression(vt.getInitializer()) : null);
        } else if (st instanceof ExpressionStatementTree) {
            ExpressionStatementTree est = (ExpressionStatementTree) st;
            out.put("kind", "expression_statement");
            out.put("expression", dumpExpression(est.getExpression()));
        } else if (st instanceof ReturnTree) {
            ReturnTree rt = (ReturnTree) st;
            out.put("kind", "return");
            out.put("expression", rt.getExpression() != null ? dumpExpression(rt.getExpression()) : null);
        } else if (st instanceof IfTree) {
            IfTree it = (IfTree) st;
            out.put("kind", "if");
            out.put("condition", dumpExpression(it.getCondition()));
            out.put("then_statement", dumpStatement(it.getThenStatement()));
            out.put("else_statement", it.getElseStatement() != null ? dumpStatement(it.getElseStatement()) : null);
        } else if (st instanceof ForLoopTree) {
            ForLoopTree flt = (ForLoopTree) st;
            out.put("kind", "for");
            List<Object> inits = new ArrayList<>();
            for (StatementTree init : flt.getInitializer()) {
                inits.add(dumpStatement(init));
            }
            out.put("initializers", inits);
            out.put("condition", flt.getCondition() != null ? dumpExpression(flt.getCondition()) : null);
            List<Object> updates = new ArrayList<>();
            for (ExpressionStatementTree up : flt.getUpdate()) {
                updates.add(dumpStatement(up));
            }
            out.put("updates", updates);
            out.put("statement", dumpStatement(flt.getStatement()));
        } else if (st instanceof EnhancedForLoopTree) {
            EnhancedForLoopTree eflt = (EnhancedForLoopTree) st;
            out.put("kind", "enhanced_for");
            out.put("variable", dumpStatement(eflt.getVariable()));
            out.put("expression", dumpExpression(eflt.getExpression()));
            out.put("statement", dumpStatement(eflt.getStatement()));
        } else if (st instanceof WhileLoopTree) {
            WhileLoopTree wlt = (WhileLoopTree) st;
            out.put("kind", "while");
            out.put("condition", dumpExpression(wlt.getCondition()));
            out.put("statement", dumpStatement(wlt.getStatement()));
        } else if (st instanceof DoWhileLoopTree) {
            DoWhileLoopTree dwlt = (DoWhileLoopTree) st;
            out.put("kind", "do_while");
            out.put("condition", dumpExpression(dwlt.getCondition()));
            out.put("statement", dumpStatement(dwlt.getStatement()));
        } else if (st instanceof BlockTree) {
            BlockTree bt = (BlockTree) st;
            out.put("kind", "block");
            List<Object> stmtList = new ArrayList<>();
            for (StatementTree inner : bt.getStatements()) {
                stmtList.add(dumpStatement(inner));
            }
            out.put("statements", stmtList);
        } else if (st instanceof TryTree) {
            TryTree tt = (TryTree) st;
            out.put("kind", "try");
            List<Object> resources = new ArrayList<>();
            for (Tree res : tt.getResources()) {
                if (res instanceof StatementTree) {
                    resources.add(dumpStatement((StatementTree) res));
                } else if (res instanceof ExpressionTree) {
                    resources.add(dumpExpression((ExpressionTree) res));
                }
            }
            out.put("resources", resources);
            out.put("block", dumpStatement(tt.getBlock()));
            List<Object> catches = new ArrayList<>();
            for (CatchTree ct : tt.getCatches()) {
                Map<String, Object> catchEntry = new LinkedHashMap<>();
                catchEntry.put("parameter_name", ct.getParameter().getName().toString());
                catchEntry.put("parameter_type", ct.getParameter().getType().toString());
                catchEntry.put("block", dumpStatement(ct.getBlock()));
                catches.add(catchEntry);
            }
            out.put("catches", catches);
            out.put("finally_block", tt.getFinallyBlock() != null ? dumpStatement(tt.getFinallyBlock()) : null);
        } else if (st instanceof ThrowTree) {
            ThrowTree tt = (ThrowTree) st;
            out.put("kind", "throw");
            out.put("expression", dumpExpression(tt.getExpression()));
        } else if (st instanceof BreakTree) {
            BreakTree bt = (BreakTree) st;
            out.put("kind", "break");
            out.put("label", bt.getLabel() != null ? bt.getLabel().toString() : null);
        } else if (st instanceof ContinueTree) {
            ContinueTree ct = (ContinueTree) st;
            out.put("kind", "continue");
            out.put("label", ct.getLabel() != null ? ct.getLabel().toString() : null);
        } else if (st instanceof SwitchTree) {
            SwitchTree stt = (SwitchTree) st;
            out.put("kind", "switch");
            out.put("expression", dumpExpression(stt.getExpression()));
            List<Object> cases = new ArrayList<>();
            for (CaseTree c : stt.getCases()) {
                Map<String, Object> caseEntry = new LinkedHashMap<>();
                caseEntry.put("source", c.toString());
                List<Object> stmts = new ArrayList<>();
                if (c.getStatements() != null) {
                    for (StatementTree s : c.getStatements()) {
                        stmts.add(dumpStatement(s));
                    }
                }
                caseEntry.put("statements", stmts);
                caseEntry.put("is_default", c.getExpression() == null && (c.getExpressions() == null || c.getExpressions().isEmpty()));
                cases.add(caseEntry);
            }
            out.put("cases", cases);
        } else if (st instanceof AssertTree) {
            AssertTree at = (AssertTree) st;
            out.put("kind", "assert");
            out.put("condition", dumpExpression(at.getCondition()));
            out.put("detail", at.getDetail() != null ? dumpExpression(at.getDetail()) : null);
        } else if (st instanceof EmptyStatementTree) {
            out.put("kind", "empty");
        } else {
            out.put("kind", "unsupported");
            out.put("node_type", st.getKind().name());
        }
        return out;
    }

    private static Map<String, Object> dumpExpression(ExpressionTree et) {
        if (et == null) return null;
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("source", et.toString());

        if (et instanceof IdentifierTree) {
            IdentifierTree it = (IdentifierTree) et;
            out.put("kind", "identifier");
            out.put("name", it.getName().toString());
        } else if (et instanceof LiteralTree) {
            LiteralTree lt = (LiteralTree) et;
            out.put("kind", "literal");
            out.put("value", lt.getValue() != null ? lt.getValue().toString() : "null");
            out.put("literal_kind", lt.getKind().name());
        } else if (et instanceof MethodInvocationTree) {
            MethodInvocationTree mit = (MethodInvocationTree) et;
            out.put("kind", "method_invocation");
            out.put("method_select", dumpExpression(mit.getMethodSelect()));
            List<Object> args = new ArrayList<>();
            for (ExpressionTree arg : mit.getArguments()) {
                args.add(dumpExpression(arg));
            }
            out.put("arguments", args);
            List<String> typeArgs = new ArrayList<>();
            for (Tree ta : mit.getTypeArguments()) {
                typeArgs.add(ta.toString());
            }
            out.put("type_arguments", typeArgs);
        } else if (et instanceof MemberSelectTree) {
            MemberSelectTree mst = (MemberSelectTree) et;
            out.put("kind", "member_select");
            out.put("expression", dumpExpression(mst.getExpression()));
            out.put("identifier", mst.getIdentifier().toString());
        } else if (et instanceof AssignmentTree) {
            AssignmentTree at = (AssignmentTree) et;
            out.put("kind", "assignment");
            out.put("variable", dumpExpression(at.getVariable()));
            out.put("expression", dumpExpression(at.getExpression()));
        } else if (et instanceof CompoundAssignmentTree) {
            CompoundAssignmentTree cat = (CompoundAssignmentTree) et;
            out.put("kind", "compound_assignment");
            out.put("operator", cat.getKind().name());
            out.put("variable", dumpExpression(cat.getVariable()));
            out.put("expression", dumpExpression(cat.getExpression()));
        } else if (et instanceof NewClassTree) {
            NewClassTree nct = (NewClassTree) et;
            out.put("kind", "object_creation");
            out.put("class_type", nct.getIdentifier().toString());
            List<Object> args = new ArrayList<>();
            for (ExpressionTree arg : nct.getArguments()) {
                args.add(dumpExpression(arg));
            }
            out.put("arguments", args);
            List<String> typeArgs = new ArrayList<>();
            for (Tree ta : nct.getTypeArguments()) {
                typeArgs.add(ta.toString());
            }
            out.put("type_arguments", typeArgs);
        } else if (et instanceof NewArrayTree) {
            NewArrayTree nat = (NewArrayTree) et;
            out.put("kind", "array_creation");
            out.put("element_type", nat.getType() != null ? nat.getType().toString() : null);
            List<Object> dims = new ArrayList<>();
            for (ExpressionTree dim : nat.getDimensions()) {
                dims.add(dumpExpression(dim));
            }
            out.put("dimensions", dims);
            List<Object> inits = new ArrayList<>();
            if (nat.getInitializers() != null) {
                for (ExpressionTree init : nat.getInitializers()) {
                    inits.add(dumpExpression(init));
                }
            }
            out.put("initializers", inits);
        } else if (et instanceof ArrayAccessTree) {
            ArrayAccessTree aat = (ArrayAccessTree) et;
            out.put("kind", "array_access");
            out.put("expression", dumpExpression(aat.getExpression()));
            out.put("index", dumpExpression(aat.getIndex()));
        } else if (et instanceof BinaryTree) {
            BinaryTree bt = (BinaryTree) et;
            out.put("kind", "binary_operation");
            out.put("operator", bt.getKind().name());
            out.put("left", dumpExpression(bt.getLeftOperand()));
            out.put("right", dumpExpression(bt.getRightOperand()));
        } else if (et instanceof UnaryTree) {
            UnaryTree ut = (UnaryTree) et;
            out.put("kind", "unary_operation");
            out.put("operator", ut.getKind().name());
            out.put("expression", dumpExpression(ut.getExpression()));
        } else if (et instanceof ParenthesizedTree) {
            ParenthesizedTree pt = (ParenthesizedTree) et;
            out.put("kind", "parenthesized");
            out.put("expression", dumpExpression(pt.getExpression()));
        } else if (et instanceof TypeCastTree) {
            TypeCastTree tct = (TypeCastTree) et;
            out.put("kind", "type_cast");
            out.put("target_type", tct.getType().toString());
            out.put("expression", dumpExpression(tct.getExpression()));
        } else if (et instanceof InstanceOfTree) {
            InstanceOfTree iot = (InstanceOfTree) et;
            out.put("kind", "instance_of");
            out.put("check_type", iot.getType().toString());
            out.put("expression", dumpExpression(iot.getExpression()));
        } else if (et instanceof ConditionalExpressionTree) {
            ConditionalExpressionTree cet = (ConditionalExpressionTree) et;
            out.put("kind", "conditional_expression");
            out.put("condition", dumpExpression(cet.getCondition()));
            out.put("true_expression", dumpExpression(cet.getTrueExpression()));
            out.put("false_expression", dumpExpression(cet.getFalseExpression()));
        } else if (et instanceof LambdaExpressionTree) {
            LambdaExpressionTree let = (LambdaExpressionTree) et;
            out.put("kind", "lambda");
            List<Object> params = new ArrayList<>();
            for (VariableTree p : let.getParameters()) {
                params.add(dumpStatement(p));
            }
            out.put("parameters", params);
            if (let.getBody() instanceof StatementTree) {
                out.put("body_statement", dumpStatement((StatementTree) let.getBody()));
            } else if (let.getBody() instanceof ExpressionTree) {
                out.put("body_expression", dumpExpression((ExpressionTree) let.getBody()));
            }
        } else if (et instanceof MemberReferenceTree) {
            MemberReferenceTree mrt = (MemberReferenceTree) et;
            out.put("kind", "member_reference");
            out.put("qualifier", mrt.getQualifierExpression().toString());
            out.put("name", mrt.getName().toString());
        } else {
            out.put("kind", "unsupported");
            out.put("node_type", et.getKind().name());
        }

        return out;
    }

    private static List<String> modifiersOf(ModifiersTree modifiers) {
        List<String> out = new ArrayList<>();
        for (javax.lang.model.element.Modifier m : modifiers.getFlags()) {
            out.add(m.toString());
        }
        return out;
    }

    private static List<String> annotationsOf(ModifiersTree modifiers) {
        List<String> out = new ArrayList<>();
        for (AnnotationTree a : modifiers.getAnnotations()) {
            out.add(a.getAnnotationType().toString());
        }
        return out;
    }

    static class Json {
        static String stringify(Object o) {
            StringBuilder sb = new StringBuilder();
            write(o, sb);
            return sb.toString();
        }

        @SuppressWarnings("unchecked")
        private static void write(Object o, StringBuilder sb) {
            if (o == null) {
                sb.append("null");
            } else if (o instanceof String) {
                writeString((String) o, sb);
            } else if (o instanceof Boolean) {
                sb.append(((Boolean) o) ? "true" : "false");
            } else if (o instanceof Number) {
                sb.append(o.toString());
            } else if (o instanceof Map) {
                sb.append("{");
                boolean first = true;
                for (Map.Entry<String, Object> e : ((Map<String, Object>) o).entrySet()) {
                    if (!first) sb.append(",");
                    first = false;
                    writeString(e.getKey(), sb);
                    sb.append(":");
                    write(e.getValue(), sb);
                }
                sb.append("}");
            } else if (o instanceof List) {
                sb.append("[");
                boolean first = true;
                for (Object item : (List<Object>) o) {
                    if (!first) sb.append(",");
                    first = false;
                    write(item, sb);
                }
                sb.append("]");
            } else {
                writeString(o.toString(), sb);
            }
        }

        private static void writeString(String s, StringBuilder sb) {
            sb.append("\"");
            for (int i = 0; i < s.length(); i++) {
                char c = s.charAt(i);
                switch (c) {
                    case '"': sb.append("\\\""); break;
                    case '\\': sb.append("\\\\"); break;
                    case '\n': sb.append("\\n"); break;
                    case '\r': sb.append("\\r"); break;
                    case '\t': sb.append("\\t"); break;
                    default:
                        if (c < 0x20) {
                            sb.append(String.format("\\u%04x", (int) c));
                        } else {
                            sb.append(c);
                        }
                }
            }
            sb.append("\"");
        }
    }
}

