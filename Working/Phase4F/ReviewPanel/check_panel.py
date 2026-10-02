"""Isolated wrapper checks. Never export or command a real human session."""
import copy
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import apose_review_core as core
import bridge


class ReviewDouble:
    def __init__(self):
        self.character = 'John'
        self.state = copy.deepcopy(core.read(HERE.parents[2] / 'Documentation/Phase4F/ReviewPanel/john_state_at_attachment.json'))
        self.controls = {r['role']: None for r in self.state['joints']}
        self.changes, self.calls = {}, []
        self.A = SimpleNamespace(get_selected_level_actors=lambda: [])
        self.map = 'test-only'

    def active(self): pass
    def pending(self): return self.changes
    def event(self, kind, details): self.state['events'].append(dict(kind=kind, details=details))
    def select(self, role):
        self.calls.append(('select', role))
        self.event('select', {'role': role})
    def view(self, name):
        self.calls.append(('view', name))
        self.event('view', {'view': name})
    def open(self, character): self.calls.append(('open', character)); self.character = character
    def start(self): self.calls.append(('start',))
    def save(self): self.calls.append(('save',))
    def finish(self): self.calls.append(('finish',))
    def record(self): self.calls.append(('record',))
    def accept(self, role): self.calls.append(('accept', role))
    def unresolved(self, role): self.calls.append(('unresolved', role))
    def track(self, side, number): self.calls.append(('track', side, number))
    def identify(self, side, digit, number): self.calls.append(('identify', side, digit, number))


class WrapperChecks(unittest.TestCase):
    def setUp(self): self.r = ReviewDouble()
    def dispatch(self, action, **args): bridge.dispatch(self.r, core, action, args)

    def test_attachment_is_read_only(self):
        before = core.digest(self.r.state)
        with tempfile.TemporaryDirectory(dir=HERE) as folder:
            original = bridge.RUNTIME
            try:
                bridge.RUNTIME = Path(folder)
                b = bridge.Bridge(self.r, core)
                b.publish()
                s = json.loads((Path(folder) / 'status.json').read_text())
                self.assertEqual(s['metrics']['currently_accepted_human_roles'], ['pelvis'])
                self.assertEqual(before, core.digest(self.r.state))
                self.assertEqual(self.r.calls, [])
            finally: bridge.RUNTIME = original

    def test_guided_step_selects_and_views(self):
        self.dispatch('step', role='neck_01')
        self.assertEqual(self.r.calls, [('select', 'neck_01'), ('view', 'side')])

    def test_unidentified_finger_does_not_infer_or_select(self):
        self.dispatch('step', role='thumb_l')
        self.assertEqual(self.r.calls, [('view', 'hand_l_top')])
        for action in ('accept', 'unresolved', 'select'):
            with self.assertRaises(ValueError):
                self.dispatch(action, role='thumb_l' if action != 'select' else 'thumb_l:root')

    def test_mutations_delegate_without_rebuilding_model(self):
        for action in ('record', 'save', 'finish'):
            self.dispatch(action)
        self.dispatch('accept', role='head')
        self.dispatch('unresolved', role='head')
        self.dispatch('accept', role='Neck / head')
        self.dispatch('identify', side='r', digit='index', number=4)
        self.assertEqual(self.r.calls, [('record',), ('save',), ('finish',),
                         ('accept', 'head'), ('unresolved', 'head'), ('accept', 'Neck / head'),
                         ('identify', 'r', 'index', 4)])

    def test_duplicate_start_and_finished_finish_rejected(self):
        with self.assertRaises(ValueError): self.dispatch('start')
        self.r.state['trial_finished_at'] = time.time()
        with self.assertRaises(ValueError): self.dispatch('finish')
        self.assertEqual(self.r.calls, [])

    def test_pending_positions_never_discarded_on_switch_or_unsure(self):
        self.r.changes = {'head': [0, 0, 150]}
        for action, args in [('open', dict(character='Jane')), ('step', dict(role='head')),
                             ('accept', dict(role='head')), ('unresolved', dict(role='head'))]:
            with self.assertRaises(ValueError): bridge.dispatch(self.r, core, action, args)
        self.assertEqual(self.r.calls, [])
        self.dispatch('open', character='John')  # Same-character open is a safe no-op.
        self.assertEqual(self.r.calls, [])

    def test_identity_must_be_explicit_and_track_valid(self):
        for digit in ('', 'guess'):
            with self.assertRaises(ValueError): self.dispatch('identify', side='l', digit=digit, number=1)
        for number in (True, 0, 6, '1'):
            with self.assertRaises(ValueError): self.dispatch('track', side='l', number=number)
        self.assertEqual(self.r.calls, [])

    def test_transport_context_expiry_and_validation_boundary(self):
        original = bridge.RUNTIME
        with tempfile.TemporaryDirectory(dir=HERE) as folder:
            try:
                bridge.RUNTIME = Path(folder)
                b = bridge.Bridge(self.r, core)
                template = dict(bridge_id=b.id, character='John', session_id=self.r.state['session_id'],
                                revision=core.digest(self.r.state), expires=time.time()+12,
                                action='step', args={'role':'head'})
                before = core.digest(self.r.state)
                def send(key, changes, validation=True):
                    data = dict(template, **changes)
                    path = Path(folder) / 'validation' / (key + '.json')
                    path.write_text(json.dumps(data))
                    b.process(path, validation)
                    self.assertFalse(path.exists())  # claimed commands cannot be replayed
                    return json.loads((Path(folder) / 'results' / path.name).read_text())
                self.assertTrue(send('navigation', {})['ok'])
                self.assertEqual(before, core.digest(self.r.state))
                self.assertTrue(callable(self.r.event))
                for key, changes in [('stale', {'revision':'old'}), ('wrong-session', {'session_id':'other'}),
                                     ('wrong-character', {'character':'Jane'}), ('expired', {'expires':0}),
                                     ('reattached', {'bridge_id':'old'}), ('no-human-approval', {'action':'accept'})]:
                    self.assertFalse(send(key, changes)['ok'])
                self.assertEqual(before, core.digest(self.r.state))
            finally: bridge.RUNTIME = original


if __name__ == '__main__': unittest.main(verbosity=2)
