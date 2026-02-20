import numpy as np

from gm_rl.adapters.local_mock import LocalMockAdapter
from gm_rl.features import FeatureConfig, FeatureEncoder


def test_feature_shapes_and_masks():
    adapter = LocalMockAdapter(seed=1)
    state = adapter.load_roster_state(seed=1)
    cfg = FeatureConfig(max_players=5, normalize_observations=False, include_pro_metrics=False)
    encoder = FeatureEncoder(cfg)
    obs = encoder.encode(state, team_id=1)

    assert obs.team.shape[0] == encoder._team_dim()
    assert obs.league.shape[0] == encoder._league_dim()
    assert obs.players.shape == (cfg.max_players, encoder._player_dim())
    assert obs.player_mask.shape == (cfg.max_players,)
    assert obs.player_mask.sum() == min(cfg.max_players, len(state.get_team(1).roster))
    assert np.all(obs.players[~obs.player_mask] == 0)


def test_nan_imputation_and_masks():
    adapter = LocalMockAdapter(seed=2)
    state = adapter.load_roster_state(seed=2)
    player = next(iter(state.players.values()))
    player.stats.fg_pct = float("nan")
    cfg = FeatureConfig(max_players=3, normalize_observations=False, impute_value=-1.0)
    encoder = FeatureEncoder(cfg)
    obs = encoder.encode(state, team_id=1)
    assert not np.isnan(obs.players).any()
    # imputed value should appear where NaN existed
    assert (-1.0 in obs.players)
