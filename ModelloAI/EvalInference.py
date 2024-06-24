import lightning as L
from collections import OrderedDict
from torch import nn
import torch
import numpy as np

#from ChessAITraining import EvaluationModel

class EvaluationModel(L.LightningModule):
    
    def __init__(self, learning_rate=1e-3, batch_size=1024, layer_count= 10):
        super().__init__()
        
        self.to('cuda')
        self.batch_size= batch_size
        self.learning_rate= learning_rate
        layers= []

        #776 neuroni per ogni strano, tranne l'ultimo
        for i in range(layer_count-1):
            layers.append((f'linear-{i}', nn.Linear(776, 776)))
            layers.append((f'relu-{i}', nn.ReLU()))
        layers.append((f'linear-{layer_count-1}', nn.Linear(776,1)))
        self.seq= nn.Sequential(OrderedDict(layers))

    def forward(self, x):
        return self.seq(x)
    


def move_eval_ai(binary):
    model= EvaluationModel.load_from_checkpoint("Predicter.ckpt", layer_count= 6)
    model.eval()

    bin= np.frombuffer(binary, dtype= np.uint8)
    bin= np.unpackbits(bin, axis=0).astype(np.single)
    ts= torch.tensor(bin, device='cuda')
    with torch.no_grad():
        y_hat = model(ts)
    
    print(y_hat)
    return float(y_hat.data[0])

