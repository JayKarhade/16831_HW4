from cs16831.hw4_part2.infrastructure import pytorch_util as ptu
from .base_exploration_model import BaseExplorationModel
import torch.optim as optim
from torch import nn
import torch

def init_method_1(model):
    model.weight.data.uniform_()
    model.bias.data.uniform_()

def init_method_2(model):
    model.weight.data.normal_()
    model.bias.data.normal_()


class RNDModel(nn.Module, BaseExplorationModel):
    def __init__(self, hparams, optimizer_spec, **kwargs):
        super().__init__(**kwargs)
        self.ob_dim = hparams['ob_dim']
        self.output_size = hparams['rnd_output_size']
        self.n_layers = hparams['rnd_n_layers']
        self.size = hparams['rnd_size']
        self.optimizer_spec = optimizer_spec

        # <TODO>: Create two neural networks:
        # 1) f, the random function we are trying to learn
        # 2) f_hat, the function we are using to learn f

        self.f = ptu.build_mlp(self.ob_dim, self.output_size, self.n_layers, self.size, init_method=init_method_1).cuda()
        self.f_hat = ptu.build_mlp(self.ob_dim, self.output_size, self.n_layers, self.size, init_method=init_method_2).cuda()

        self.optimizer = self.optimizer_spec.constructor(
            self.f_hat.parameters(),
            **self.optimizer_spec.optim_kwargs
        )

    def forward(self, ob_no):
        # <TODO>: Get the prediction error for ob_no
        # HINT: Remember to detach the output of self.f!
        # pass

        target = self.f(ob_no).detach()
        prediction = self.f_hat(ob_no)

        return torch.norm(target - prediction, dim=1)

    def forward_np(self, ob_no):
        ob_no = ptu.from_numpy(ob_no)
        error = self(ob_no)
        return ptu.to_numpy(error)

    def update(self, ob_no):
        # <TODO>: Update f_hat using ob_no
        # Hint: Take the mean prediction error across the batch
        # pass
        ob_no = ptu.from_numpy(ob_no)
        error = self.forward(ob_no)
        loss = torch.mean(error)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
    