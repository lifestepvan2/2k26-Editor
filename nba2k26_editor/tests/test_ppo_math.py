import numpy as np
import torch

from gm_rl.actions import ActionMask, ActionSpaceSpec
from gm_rl.ppo import PPOConfig, RolloutBuffer


def _dummy_obs():
    return {
        "team": np.zeros((1, 2), dtype=np.float32),
        "players": np.zeros((1, 2, 3), dtype=np.float32),
        "player_mask": np.ones((1, 2), dtype=bool),
        "league": np.zeros((1, 2), dtype=np.float32),
    }


def _dummy_mask(spec: ActionSpaceSpec):
    return ActionMask(
        draft=torch.ones((spec.draft_slots,), dtype=torch.bool),
        trade=torch.ones((spec.trade_candidates,), dtype=torch.bool),
        rotation=torch.ones((spec.rotation_templates,), dtype=torch.bool),
        contract=torch.ones((spec.contract_candidates,), dtype=torch.bool),
        roster_move=torch.ones((spec.roster_moves,), dtype=torch.bool),
    )


def test_gae_shapes_and_last_step():
    cfg = PPOConfig(rollout_steps=4, n_envs=1, normalize_advantages=False, gamma=0.99, gae_lambda=0.95)
    spec = ActionSpaceSpec()
    obs_shapes = {"team": (2,), "players": (2, 3), "league": (2,), "player_mask": (2,)}
    buffer = RolloutBuffer(cfg, obs_shapes, spec, torch.device("cpu"))

    dummy_obs = _dummy_obs()
    mask = _dummy_mask(spec)
    for t in range(cfg.rollout_steps):
        buffer.add(
            obs=dummy_obs,
            actions=torch.zeros((1, len(spec.sizes)), dtype=torch.long),
            log_probs=torch.zeros(1),
            rewards=np.array([1.0], dtype=np.float32),
            dones=np.array([1.0 if t == cfg.rollout_steps - 1 else 0.0]),
            values=torch.zeros(1),
            masks=[mask],
        )

    advantages, returns = buffer.compute_returns_and_advantages(torch.zeros(1), cfg.gamma, cfg.gae_lambda)
    assert advantages.shape == (cfg.rollout_steps, cfg.n_envs)
    assert returns.shape == (cfg.rollout_steps, cfg.n_envs)
    # last step should equal immediate reward when done
    assert torch.isclose(advantages[-1, 0], torch.tensor(1.0))
    assert torch.isclose(returns[-1, 0], torch.tensor(1.0))
