from gm_rl.actions import ActionMaskBuilder, ActionSpaceSpec
from gm_rl.adapters.local_mock import LocalMockAdapter


def test_draft_mask_blocks_full_roster():
    adapter = LocalMockAdapter(seed=3)
    state = adapter.load_roster_state(seed=3)
    builder = ActionMaskBuilder(ActionSpaceSpec())
    mask = builder.build(state, team_id=1)
    # Mock teams start at max roster -> draft should be blocked
    assert mask.draft.sum() == 0


def test_roster_move_mask_respects_minimum():
    adapter = LocalMockAdapter(seed=4)
    state = adapter.load_roster_state(seed=4)
    team = state.get_team(1)
    team.roster = team.roster[: state.context.minimum_roster]
    builder = ActionMaskBuilder(ActionSpaceSpec())
    mask = builder.build(state, team_id=1)
    # waives/signs disallowed when at minimum roster
    assert not mask.roster_move[1:].any()
