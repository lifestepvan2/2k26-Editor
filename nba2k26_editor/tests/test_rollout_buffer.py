import numpy as np
import torch

from gm_rl.actions import ActionMask, ActionSpaceSpec
from gm_rl.ppo import PPOConfig, RolloutBuffer


def make_mask(spec: ActionSpaceSpec) -> ActionMask:
    return ActionMask(
        draft=torch.ones((spec.draft_slots,), dtype=torch.bool),
        trade=torch.ones((spec.trade_candidates,), dtype=torch.bool),
        rotation=torch.ones((spec.rotation_templates,), dtype=torch.bool),
        contract=torch.ones((spec.contract_candidates,), dtype=torch.bool),
        roster_move=torch.ones((spec.roster_moves,), dtype=torch.bool),
    )


def test_rollout_buffer_ordering_and_dones():
    cfg = PPOConfig(rollout_steps=3, n_envs=1, normalize_advantages=False)
    spec = ActionSpaceSpec()
    obs_shapes = {"team": (2,), "players": (1, 2), "league": (1,), "player_mask": (1,)}
    buffer = RolloutBuffer(cfg, obs_shapes, spec, torch.device("cpu"))
    mask = make_mask(spec)
    for t in range(cfg.rollout_steps):
        buffer.add(
            obs={"team": np.zeros((1, 2)), "players": np.zeros((1, 1, 2)), "player_mask": np.ones((1, 1), dtype=bool), "league": np.zeros((1, 1))},
            actions=torch.full((1, len(spec.sizes)), t, dtype=torch.long),
            log_probs=torch.zeros(1),
            rewards=np.array([float(t)], dtype=np.float32),
            dones=np.array([1.0 if t == cfg.rollout_steps - 1 else 0.0]),
            values=torch.zeros(1),
            masks=[mask],
        )
    assert torch.equal(buffer.actions[:, 0, 0], torch.tensor([0, 1, 2]))
    advantages, returns = buffer.compute_returns_and_advantages(torch.zeros(1), cfg.gamma, cfg.gae_lambda)
    assert advantages.shape[0] == cfg.rollout_steps
    assert returns[-1, 0] == cfg.rollout_steps - 1
