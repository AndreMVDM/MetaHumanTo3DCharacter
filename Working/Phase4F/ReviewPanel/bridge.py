"""Main-thread usability adapter for the existing, live Phase4F Review object.

No session initialisation, core export or approval mutation happens on attachment.
Only explicit human commands invoke evidence-writing backend methods.
"""
import json
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / 'runtime'
VIEWS = ('front', 'side', 'arms', 'pelvis', 'feet',
         'hand_l_top', 'hand_l_front', 'hand_r_top', 'hand_r_front')


def steps(core):
    result = []
    groups = [
        ('Pelvis / hips', [('pelvis', 'pelvis')]),
        ('Spine / neck / head', [(n, 'side') for n in
          ('spine_01', 'spine_02', 'spine_03', 'neck_01', 'head')]),
    ]
    for side, label in [('l', 'Left'), ('r', 'Right')]:
        groups.append((label + ' arm', [(n + '_' + side, 'arms') for n in
                      ('upperarm', 'clavicle', 'lowerarm', 'hand')]))
    for side, label in [('l', 'Left'), ('r', 'Right')]:
        groups.append((label + ' leg', [(n + '_' + side, 'feet' if n in ('foot', 'ball') else 'front')
                                      for n in ('thigh', 'calf', 'foot', 'ball')]))
    for group, roles in groups:
        for role, view in roles:
            result.append(dict(kind='body', role=role, group=group, view=view,
                               label=core.LABELS.get(role, role.replace('_', ' ').title())))
    for side, label in [('l', 'Left'), ('r', 'Right')]:
        for digit in core.DIGITS:
            result.append(dict(kind='finger', role=digit + '_' + side,
                               side=side, digit=digit, group=label + ' fingers',
                               label=label + ' ' + digit, view='hand_' + side + '_top'))
    result.extend([dict(kind='summary', label='Review summary', group='Summary'),
                   dict(kind='validation', label='Anatomy validation', group='Validation')])
    return result


def dispatch(review, core, action, args):
    """The only mutation route: call exactly the existing backend methods."""
    if action == 'refresh':
        return
    if action == 'open':
        character = args['character']
        if character not in ('John', 'Jane'):
            raise ValueError('Choose John or Jane')
        if character != review.character:
            # Check before open(): its existing callback is removed before its own guard.
            if review.pending():
                raise ValueError('Record pending gizmo placements before changing character')
            review.open(character)
        return
    review.active()
    if action == 'start':
        if core.metrics(review.state)['trial_status'] == 'in_progress':
            raise ValueError('This trial is already in progress; continue reviewing')
        review.start()
    elif action in ('save', 'finish', 'record'):
        if action == 'finish' and core.metrics(review.state)['trial_status'] != 'in_progress':
            raise ValueError('Only an in-progress trial can be finished')
        getattr(review, action)()
    elif action == 'select':
        if args['role'] not in review.controls:
            raise ValueError('Identify this finger track before selecting its root or tip')
        review.select(args['role'])
    elif action == 'view':
        if args['view'] not in VIEWS:
            raise ValueError('Unknown review view')
        review.view(args['view'])
    elif action == 'step':
        step = next((s for s in steps(core) if s.get('role') == args['role']), None)
        if step is None:
            raise ValueError('Unknown guided step')
        if review.pending():
            raise ValueError('Record pending placements before changing step')
        if step['kind'] == 'body':
            review.select(step['role'])
        elif step['role'] in review.state['fingers']:
            review.select(step['role'] + ':root')
        review.view(step['view'])
    elif action in ('accept', 'unresolved'):
        # unresolved() redraws too; never silently discard an exploratory gizmo move.
        if review.pending():
            raise ValueError('Record pending gizmo placements before Accept or Unsure')
        role = args['role']
        valid = {r['role'] for r in review.state['joints'] if r['role'] != 'root'}
        valid.update(review.state['fingers'])
        if role not in valid and role not in core.GROUPS:
            raise ValueError('Identify this named finger before reviewing its chain')
        getattr(review, action)(role)
    elif action == 'track':
        check_hand(args)
        review.track(args['side'], args['number'])
    elif action == 'identify':
        check_hand(args)
        if args['digit'] not in core.DIGITS:
            raise ValueError('Explicitly choose the digit identity after inspecting the track')
        review.identify(args['side'], args['digit'], args['number'])
    else:
        raise ValueError('Unknown panel action')


def check_hand(args):
    if args['side'] not in ('l', 'r') or type(args['number']) is not int or args['number'] not in range(1, 6):
        raise ValueError('Choose left/right and track 1–5')


class Bridge:
    def __init__(self, review, core):
        self.review, self.core = review, core
        self.id = uuid.uuid4().hex
        self.handle = None
        self.last_publish = 0
        self.selected_step = None
        RUNTIME.mkdir(exist_ok=True)
        for name in ('commands', 'claimed', 'results', 'validation'):
            (RUNTIME / name).mkdir(exist_ok=True)

    def snapshot(self):
        r, c = self.review, self.core
        r.active()
        return dict(bridge_id=self.id, heartbeat=time.time(), character=r.character,
                    session_id=r.state['session_id'], revision=c.digest(r.state),
                    metrics=c.metrics(r.state), pending=r.pending(),
                    fingers=r.state['fingers'], controls=list(r.controls),
                    selected_controls=[a.get_actor_label()[11:] for a in r.A.get_selected_level_actors()
                                       if a.get_actor_label().startswith('F4 CONTROL ')],
                    labels=c.LABELS, groups=c.GROUPS, steps=steps(c),
                    selected_step=self.selected_step, map=r.map)

    def publish(self):
        try:
            data = self.snapshot()
        except Exception as exc:
            data = dict(bridge_id=self.id, heartbeat=time.time(), error=str(exc))
        self.core.save(RUNTIME / 'status.json', data)

    def process(self, path, validation=False):
        # Claim before executing. Interrupted commands are never automatically replayed.
        claimed = RUNTIME / 'claimed' / path.name
        path.replace(claimed)
        data = json.loads(claimed.read_text(encoding='utf-8'))
        result = dict(id=path.stem, action=data.get('action'), ok=False)
        try:
            if data.get('bridge_id') != self.id or time.time() > data['expires']:
                raise ValueError('Command expired or editor reattached; refresh and try again')
            r = self.review
            if data.get('character') != r.character or data.get('session_id') != r.state['session_id']:
                raise ValueError('Character changed; refresh before issuing another command')
            if data.get('revision') != self.core.digest(r.state):
                raise ValueError('Review changed since this command; refresh and try again')
            action, args = data['action'], data.get('args', {})
            if validation:
                if action not in ('open', 'refresh', 'select', 'view', 'step', 'track'):
                    raise ValueError('Validation can only navigate; no review, identity or placement commands')
                # Exercise the SAME backend navigation methods without posing as the human.
                # No core export, state changes or synthetic provenance enters the real ledger.
                original_event = r.event
                try:
                    r.event = lambda *a, **k: None
                    dispatch(r, self.core, action, args)
                finally:
                    r.event = original_event
            else:
                dispatch(r, self.core, action, args)
            if action in ('step', 'select'):
                self.selected_step = args['role'].split(':')[0]
            if action == 'open':
                self.selected_step = None
            result.update(ok=True, message='Completed', character=r.character)
        except Exception as exc:
            result['message'] = str(exc)
        self.core.save(RUNTIME / 'results' / path.name, result)
        self.publish()

    def tick(self, dt):
        if time.time() - self.last_publish < .4:
            return
        self.last_publish = time.time()
        try:
            for folder, validation in [('commands', False), ('validation', True)]:
                paths = sorted((RUNTIME / folder).glob('*.json'))
                if paths:
                    self.process(paths[0], validation)
                    return
            self.publish()
        except Exception as exc:
            # Report transport failures without retrying a claimed evidence-writing action.
            self.core.save(RUNTIME / 'transport_error.json', {'error': str(exc), 'time': time.time()})


def attach():
    import builtins
    import unreal
    import apose_ue_review as backend
    old = getattr(builtins, 'phase4f_panel_bridge', None)
    if old and old.handle is not None:
        unreal.unregister_slate_post_tick_callback(old.handle)
    # Reuse the live review. Do not reload backend or call open/start/export on attachment.
    b = Bridge(backend.rigreview, backend.core)
    b.publish()
    b.handle = unreal.register_slate_post_tick_callback(b.tick)
    builtins.phase4f_panel_bridge = b
    print('PHASE4F_PANEL_ATTACHED http://127.0.0.1:8746')
    return b
