"""Execute accepted R2 code with profile/evidence-path bindings only.

The executable R2 source remains byte-for-byte untouched. AST equivalence after
normalising its single evidence-directory literal certifies unchanged logic.
No bone, operation, threshold, support or mapping statement is changed.
"""
import ast, hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
O = R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3/Initial'
O.mkdir(exist_ok=True)
import unreal
kind = 'playback' if '-r3-playback' in unreal.SystemLibrary.get_command_line() else 'author'
source = R/('Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2/'+kind+'.py')
old_literal = 'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd'
new_literal = O.relative_to(R).as_posix()
original = ast.parse(source.read_text())
count = 0
class EvidencePath(ast.NodeTransformer):
    def visit_Constant(self, node):
        global count
        if node.value == old_literal:
            count += 1
            return ast.copy_location(ast.Constant(value=new_literal), node)
        return node
bound = EvidencePath().visit(ast.parse(source.read_text()))
assert count == 1, 'Unexpected accepted R2 path bindings'
class Normalise(ast.NodeTransformer):
    def visit_Constant(self, node):
        if node.value in [old_literal,new_literal]:
            return ast.copy_location(ast.Constant(value='<PROFILE_EVIDENCE_DIRECTORY>'),node)
        return node
expected = ast.dump(Normalise().visit(original), include_attributes=False)
actual = ast.dump(Normalise().visit(ast.parse(ast.unparse(bound))), include_attributes=False)
assert expected == actual, 'R2 executable logic changed'
evidence = dict(stage=kind, accepted_source=source.relative_to(R).as_posix(), accepted_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), profile_sha256=hashlib.sha256((W/'config.json').read_bytes()).hexdigest(), algorithm_ast_sha256=hashlib.sha256(expected.encode()).hexdigest(), algorithm_unchanged=True, only_executable_binding_change=dict(evidence_directory=new_literal), input_output_paths='Separate R3 config.json; __file__ points to this run profile directory')
(O/(kind+'_execution_identity.json')).write_text(json.dumps(evidence,indent=2)+'\n')
scope = dict(__file__=str(W/'execute_r2.py'),__name__='__main__')
try:
    exec(compile(ast.fix_missing_locations(bound),str(source),'exec'),scope)
except Exception:
    if kind == 'playback':
        diagnosis = {k: sorted(scope[k]) if isinstance(scope.get(k),set) else scope.get(k) for k in ['seeds','seen','edges','foreign','authoring']}
        (O/'first_failure_context.json').write_text(json.dumps(diagnosis,indent=2)+'\n')
    raise
