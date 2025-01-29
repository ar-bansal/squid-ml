import torch
import torch.nn as nn
import torch.optim as optim
from torchmetrics import Accuracy
from pytorch_lightning import LightningModule, LightningDataModule, Trainer
from torch.utils.data import Dataset, DataLoader, random_split


def create_trainer(n_epochs: int=None) -> Trainer:
    trainer = Trainer(
            max_epochs=n_epochs, 
            logger=False, 
            enable_checkpointing=False
        )
    return trainer


class TensorDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class TensorDataModule(LightningDataModule):
    def __init__(self, X, y, batch_size=10, val_split=0.2, test_split=0.1):
        super().__init__()

        self.X = X
        self.y = y
        self.batch_size = batch_size
        self.val_split = val_split
        self.test_split = test_split

    def setup(self, stage=None):
        dataset = TensorDataset(self.X, self.y)

        total_size = len(dataset)
        val_size = int(self.val_split * total_size)
        test_size = int(self.test_split * total_size)
        train_size = total_size - val_size - test_size

        self.train_dataset, self.val_dataset, self.test_dataset = random_split(
            dataset, [train_size, val_size, test_size]
        )

    def train_dataloader(self):
        return DataLoader(
            self.train_dataset, 
            batch_size=self.batch_size, 
            shuffle=True
        )
    
    def val_dataloader(self):
        return DataLoader(
            self.val_dataset, 
            batch_size=self.batch_size
        )
    
    def test_dataloader(self):
        return DataLoader(
            self.test_dataset, 
            batch_size=self.batch_size
        )
    

class Model(LightningModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.loss_fn = nn.CrossEntropyLoss()
        self.accuracy_fn = Accuracy("multiclass", num_classes=2)

    def training_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(x)

        train_loss = self.loss_fn(outputs, y)
        train_acc = self.accuracy_fn(outputs, y)

        self.log("train_loss", train_loss, on_step=False, on_epoch=True)
        self.log("train_acc", train_acc, on_step=False, on_epoch=True)

        return train_loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        outputs = self(x)

        val_loss = self.loss_fn(outputs, y)
        val_accuracy = self.accuracy_fn(outputs, y)

        self.log("val_loss", val_loss, on_step=False, on_epoch=True)
        self.log("val_accuracy", val_accuracy,on_step=False, on_epoch=True)

    def test_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
    
        pred_labels = torch.argmax(logits, dim=1)

        test_acc = self.accuracy_fn(pred_labels, y)

        self.log("test_acc", test_acc, on_step=False, on_epoch=True)

        return test_acc
    
    def predict_step(self, batch, batch_idx):
        logits = self(batch)

        pred_labels = torch.argmax(logits, dim=1)

        return pred_labels
    
    def configure_optimizers(self):
        return optim.SGD(self.parameters(), lr=1e-3)
    

class NeuralNetwork(Model):
    def __init__(self):
        super().__init__()

        self.fc1 = nn.Sequential(
            nn.Linear(10, 4), 
        )
        self.fc2 = nn.Sequential(
            nn.Linear(4, 2)
        )
        self.relu = nn.ReLU()


    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)

        return x
