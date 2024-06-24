from peewee import *
import base64
import os
import torch
import numpy as np
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, IterableDataset, random_split
import pytorch_lightning as pl
from random import randrange
import time
from collections import OrderedDict

DB= SqliteDatabase('ChessPositions.db')

class Evaluations(Model):
    id= IntegerField()
    fen= TextField()
    binary= BlobField()
    eval= FloatField()

    class Meta:
        database= DB

    def binary_base64(self):
        return base64.b64encode(self.binary)

class EvaluationDataset(IterableDataset):
    
    def __init__(self, count):
        self.count= count
    
    def __iter__(self):
        return self
    
    def __next__(self):
        idx= randrange(self.count)
        return self[idx]
    
    def __len__(self):
        return self.count
    
    def __getitem__(self, index):
        eval= Evaluations.get(Evaluations.id == index+1)
        bin= np.frombuffer(eval.binary, dtype= np.uint8)
        bin= np.unpackbits(bin, axis=0).astype(np.single)
        eval.eval= max(eval.eval, -1500)
        eval.eval= min(eval.eval, 1500)
        ev= np.array([eval.eval]).astype(np.single)
        return {'binary': bin, 'eval': ev}
    
class EvaluationModel(pl.LightningModule):
    
    def __init__(self, learning_rate=1e-3, batch_size=1024, layer_count= 6):
        super().__init__()
        
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
    
    def training_step(self, batch, batch_idx):
        x, y= batch['binary'], batch['eval']
        y_hat= self(x)
        loss= F.l1_loss(y_hat, y)
        self.log("training_loss", loss)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)
    
    def train_dataloader(self):
        dataset= EvaluationDataset(count=LABEL_COUNT)
        return DataLoader(dataset, batch_size=self.batch_size, num_workers=2,
                           pin_memory= True)
    


DB.connect()
LABEL_COUNT= 105090749
print(LABEL_COUNT)
eval= Evaluations.get(Evaluations.id == 1)
print(eval.binary_base64())

dataset= EvaluationDataset(count= LABEL_COUNT)

configs= {
    {"layer_count": 4, "batch_size": 512},
}