from __future__ import annotations

import torch

from gm_rl.actions import ActionMask
from gm_rl.runtime import AgentRuntime
from gm_rl.ppo import PPOTrainer


def test_runtime_mask_from_info_smoke():
    info = {
        "draft": [True, False, True],
        "trade": [True, False],
        "rotation": [True, True, False],
        "contract": [False, True, True],
        "roster_move": [True, False, False],
    }
    mask = AgentRuntime._mask_from_info(info, torch.device("cpu"))
    assert mask.draft.shape == (1, 3)
    assert mask.trade.shape == (1, 2)


def test_ppo_mask_stack_smoke():
    masks = [
        ActionMask(
            draft=torch.tensor([True, False]),
            trade=torch.tensor([True, True]),
            rotation=torch.tensor([False, True]),
            contract=torch.tensor([True, False]),
            roster_move=torch.tensor([False, False]),
        ),
        ActionMask(
            draft=torch.tensor([False, True]),
            trade=torch.tensor([True, False]),
            rotation=torch.tensor([True, True]),
            contract=torch.tensor([False, True]),
            roster_move=torch.tensor([True, False]),
        ),
    ]
    stacked = PPOTrainer._stack_action_masks(masks, torch.device("cpu"))
    assert stacked.draft.shape == (2, 2)
    assert stacked.rotation.shape == (2, 2)

