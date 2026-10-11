"""
PyTorch Deep Autoencoder Architectures:
1. LSTM-AE (Sequence Recurrent Autoencoder)
2. GRU-AE (Sequence Recurrent Autoencoder)
3. Dense-AE (Non-Recurrent Deep Autoencoder)
"""

import torch
import torch.nn as nn

class DenseAutoencoder(nn.Module):
    def __init__(self, input_dim=39, hidden_dims=[64, 32, 16]):
        super(DenseAutoencoder, self).__init__()
        # Encoder
        encoder_layers = []
        in_dim = input_dim
        for h in hidden_dims:
            encoder_layers.append(nn.Linear(in_dim, h))
            encoder_layers.append(nn.BatchNorm1d(h))
            encoder_layers.append(nn.ReLU())
            in_dim = h
        self.encoder = nn.Sequential(*encoder_layers)

        # Decoder
        decoder_layers = []
        rev_dims = list(reversed(hidden_dims[:-1])) + [input_dim]
        in_dim = hidden_dims[-1]
        for idx, h in enumerate(rev_dims):
            decoder_layers.append(nn.Linear(in_dim, h))
            if idx < len(rev_dims) - 1:
                decoder_layers.append(nn.BatchNorm1d(h))
                decoder_layers.append(nn.ReLU())
            in_dim = h
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed

class LSTMAutoencoder(nn.Module):
    def __init__(self, input_dim=39, hidden_dim=64, num_layers=2):
        super(LSTMAutoencoder, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Encoder: (Batch, SeqLen, Features) -> (Batch, Hidden)
        self.encoder = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0
        )
        
        # Decoder: (Batch, SeqLen, Hidden) -> (Batch, SeqLen, Features)
        self.decoder = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0
        )
        self.output_layer = nn.Linear(hidden_dim, input_dim)

    def forward(self, x):
        # x shape: (Batch, SeqLen, Features)
        seq_len = x.size(1)
        _, (hn, _) = self.encoder(x)
        
        # Take the top layer hidden state as context vector
        context = hn[-1].unsqueeze(1).repeat(1, seq_len, 1) # (Batch, SeqLen, Hidden)
        
        dec_out, _ = self.decoder(context)
        reconstructed = self.output_layer(dec_out)
        return reconstructed

class GRUAutoencoder(nn.Module):
    def __init__(self, input_dim=39, hidden_dim=64, num_layers=2):
        super(GRUAutoencoder, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.encoder = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0
        )
        self.decoder = nn.GRU(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0
        )
        self.output_layer = nn.Linear(hidden_dim, input_dim)

    def forward(self, x):
        seq_len = x.size(1)
        _, hn = self.encoder(x)
        context = hn[-1].unsqueeze(1).repeat(1, seq_len, 1)
        dec_out, _ = self.decoder(context)
        reconstructed = self.output_layer(dec_out)
        return reconstructed
