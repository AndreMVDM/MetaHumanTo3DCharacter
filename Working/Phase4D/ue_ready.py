"""Load final shared logic without rebuilding/resetting the saved correction scene."""
import builtins,importlib
import core
importlib.reload(core)
tool=builtins.phase4d_tool
tool.state=core.rebuild(tool.state)
core.export(tool.state)
assert tool.U.get_editor_world().get_path_name().startswith('/Game/MetaHumanTo3DCharacter/Phase4D/Maps/L_GuidedCorrection')
tool.redraw();tool.view('front')
assert tool.L.save_current_level()
tool.publish('Ready. Start measured trial; record only necessary placements and explicit anatomical reviews.')
print('PHASE4D_READY',len(tool.state['events']),'events;',len(tool.state['approvals']),'approvals')
