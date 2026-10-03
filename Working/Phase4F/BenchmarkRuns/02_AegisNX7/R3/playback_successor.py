"""Audited R3 successor: accepted R2 native proof plus typed appearance gate.

The accepted source is not edited. Only its evidence directory and one foreign
ownership assignment are replaced in memory. All motion/scale/reload tests and
the independent authoring-dependency rejection remain identical.
"""
import ast, hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
W = Path(__file__).resolve().parent
R = W.parents[4]
sys.path.insert(0, str(W))
import unreal
from runtime_appearance_closure import certify_native, VERSION
female = '-r3-female-regression' in unreal.SystemLibrary.get_command_line()
final = '-r3-final-policy' in unreal.SystemLibrary.get_command_line()
folder = ('FemaleFinal' if female else 'Final') if final else ('FemaleRegression' if female else 'Corrected')
O = R/'Documentation/Phase4F/Benchmark/Runs/02_AegisNX7/R3'/folder
O.mkdir(exist_ok=True)
source = R/'Working/Phase4F/BenchmarkRuns/01_FemaleBodyRigged/R2/playback.py'
old_path = 'Documentation/Phase4F/Benchmark/Runs/01_FemaleBodyRigged/R2_EndToEnd'
new_path = O.relative_to(R).as_posix()
original = ast.parse(source.read_text())
expected_assignment = "foreign = [p for p in seen if p.startswith('/Game/') and not p.startswith(B+'/') and p not in destination_seeds]"
replacement = "appearance_certificate = _certify_native(mesh, seeds, seen, edges, reg)\nforeign = appearance_certificate['foreign_game_packages']\nresult['appearance_ownership_certificate'] = appearance_certificate"
class Bind(ast.NodeTransformer):
    paths = 0
    gates = 0
    def visit_Constant(self, node):
        if node.value == old_path:
            self.paths += 1
            return ast.copy_location(ast.Constant(new_path),node)
        return node
    def visit_Assign(self, node):
        if ast.dump(node,include_attributes=False) == ast.dump(ast.parse(expected_assignment).body[0],include_attributes=False):
            self.gates += 1
            return ast.parse(replacement).body
        return self.generic_visit(node)
bind = Bind()
bound = bind.visit(ast.parse(source.read_text()))
assert bind.paths == bind.gates == 1, 'Accepted R2 gate shape changed'
# Independently reconstruct expected entire successor from the accepted tree.
expected = source.read_text().replace(repr(old_path),repr(new_path))
assert expected.count(expected_assignment) == 1
expected = expected.replace(expected_assignment,replacement.replace('\n','\n    '))
assert ast.dump(ast.parse(expected),include_attributes=False) == ast.dump(bound,include_attributes=False)
evidence = dict(policy_version=VERSION, accepted_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    successor_ast_sha256=hashlib.sha256(ast.dump(bound,include_attributes=False).encode()).hexdigest(),
    helper_sha256=hashlib.sha256((W/'runtime_appearance_closure.py').read_bytes()).hexdigest(),
    modified_accepted_source=False, input_assets_reauthored=False,
    changes=[dict(binding='evidence_directory',value=new_path),dict(replaced=expected_assignment,with_statement=replacement)],
    all_other_R2_statements_unchanged=True)
(O/'playback_execution_identity.json').write_text(json.dumps(evidence,indent=2)+'\n')
scope = dict(__file__=str(W/'playback_successor.py'),__name__='__main__',_certify_native=certify_native)
exec(compile(ast.fix_missing_locations(bound),str(source),'exec'),scope)
