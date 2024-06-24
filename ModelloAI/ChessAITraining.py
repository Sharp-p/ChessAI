from peewee import *
import base64, os, sys, torch, time, chess
import numpy as np
from torch import nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, IterableDataset, random_split
#import pytorch_lightning as pl
import lightning as L
from lightning.pytorch.callbacks import ModelCheckpoint, RichProgressBar, Timer
from lightning.pytorch.loggers import TensorBoardLogger
from random import randrange
from collections import OrderedDict
from IPython.display import display, SVG
from datetime import timedelta
import matplotlib.pyplot as plt
""" import pysvg.sructures
import pysvg.builders
import pysvg.text """

def restart():
    os.execv(sys.executable, [os.path.basename(sys.executable)] + sys.argv)

DB= SqliteDatabase('ChessPositions.db')
SVG_BASE_URL= "https://us-central1-spearsx.cloudfunctions.net/chesspic-fen-image/"
LABEL_COUNT= 104575486

class Position(Model):
    
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
        eval= Position.get(Position.id == index+1)
        bin= np.frombuffer(eval.binary, dtype= np.uint8)
        bin= np.unpackbits(bin, axis=0).astype(np.single)
        eval.eval= max(eval.eval, -1500)
        eval.eval= min(eval.eval, 1500)
        ev= np.array([eval.eval]).astype(np.single)
        return {'binary': bin, 'eval': ev}
    
class EvaluationModel(L.LightningModule):
    
    def __init__(self, learning_rate=1e-3, batch_size=1024, layer_count= 10):
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

dataset= EvaluationDataset(count= LABEL_COUNT)

configs= [
    {"layer_count": 6, "batch_size": 16},
    #{"layer_count": 6, "batch_size": 1024}
]
train= False #flag per se training o test
if train:
    for config in configs:
        version_name= f'{int(time.time())}-batch_size-{config["batch_size"]}\
    -layer_count-{config["layer_count"]}'
        logger= TensorBoardLogger("lightning_logs", name="chessml",
                                            version=version_name)
        f= [x for x in os.listdir()]
        if not f:
            checkpoint_model = ModelCheckpoint(dirpath= "ckpt/", every_n_train_steps= 1)
        trainer= L.Trainer(precision= 16, max_epochs= 1, logger= logger, 
                            callbacks= [checkpoint_model], max_time= "00:02:00:00")
        model= EvaluationModel(layer_count=config["layer_count"], 
                            batch_size=config["batch_size"], learning_rate=1e-3)
        print("Sono arrivato qua")
        
        try:
            trainer.fit(model, )
        except Exception as exc:
            print("Sto ristartando")
            #restart()
        print("E qua pure")

model= EvaluationModel.load_from_checkpoint("Predicter.ckpt", layer_count= configs[0]['layer_count'])
model.eval()

def svg_url(fen):
    fen_board= fen.split()[0]
    return SVG_BASE_URL + fen_board

def show_index(idx):
    eval= Position.select().where(Position.id == idx+1).get()
    batch= dataset[idx]
    x, y= torch.tensor(batch['binary'], device= "cuda"), torch.tensor(batch['eval'], device= "cuda")
    y_hat= model(x)
    loss= F.l1_loss(y_hat, y)
    print(f'Idx {idx} Eval {y.data[0]:.2f} \
Prediction {y_hat.data[0]:.2f} Loss {loss:.2f}')
    print(f'FEN {eval.fen}')
    display(SVG(url=svg_url(eval.fen)))

for i in range(5):
    idx= randrange(LABEL_COUNT)
    show_index(idx)

MATERIAL_LOOKUP = {chess.KING:0,chess.QUEEN:9,chess.ROOK:5,chess.BISHOP:3,chess.KNIGHT:3,chess.PAWN:1}

def avg(lst):
    return sum(lst) / len(lst)

def material_for_board(board):
  eval = 0.0
  for sq, piece in board.piece_map().items():
    mat = MATERIAL_LOOKUP[piece.piece_type] * 100
    if piece.color == chess.BLACK:
      mat = mat * -1
    eval += mat
  return eval
  
def guess_zero_loss(idx):
  eval = Position.select().where(Position.id == idx+1).get()
  y = torch.tensor(eval.eval)
  y_hat = torch.zeros_like(y)
  loss = F.l1_loss(y_hat, y)
  return loss

def guess_material_loss(idx):
  eval = Position.select().where(Position.id == idx+1).get()
  board = chess.Board(eval.fen)
  y = torch.tensor(eval.eval)
  y_hat = torch.tensor(material_for_board(board))
  loss = F.l1_loss(y_hat, y)
  return loss

def guess_model_loss(idx):
  eval = Position.select().where(Position.id == idx+1).get()
  batch = dataset[idx]
  x, y = torch.tensor(batch['binary'], device='cuda'), torch.tensor(batch['eval'], device='cuda')
  y_hat = model(x)
  loss = F.l1_loss(y_hat, y)
  return loss

zero_losses = []
mat_losses = []
model_losses = []
for i in range(100):
  idx = randrange(LABEL_COUNT)
  zero_losses.append(guess_zero_loss(idx))
  mat_losses.append(guess_material_loss(idx))
  model_losses.append(guess_model_loss(idx))
print(f'Guess Zero Avg Loss {avg(zero_losses)}')
print(f'Guess Material Avg Loss {avg(mat_losses)}')
print(f'Guess Model Avg Loss {avg(model_losses)}')