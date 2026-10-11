"""
Main Baseline Model Training & Evaluation Script (Unbuffered Flush Output)
Trains: Dense-AE, LSTM-AE, GRU-AE, Isolation Forest, XGBoost Oracle
Saves model checkpoints, reconstruction errors, and raw baseline metrics.
"""

import os
import sys
import json
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import joblib

sys.path.append(os.path.abspath('.'))

from src.detection.autoencoders import DenseAutoencoder, LSTMAutoencoder, GRUAutoencoder
from src.detection.baselines import train_isolation_forest, evaluate_isolation_forest, train_xgboost_oracle, predict_xgboost_oracle

def create_sequences(data, seq_len=10):
    n_samples, n_features = data.shape
    num_seqs = n_samples - seq_len + 1
    seqs = np.zeros((num_seqs, seq_len, n_features), dtype=np.float32)
    for i in range(num_seqs):
        seqs[i] = data[i:i+seq_len]
    return seqs

def train_dense_ae(X_train, X_val, device, epochs=10, batch_size=512, lr=0.001, seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = DenseAutoencoder(input_dim=X_train.shape[1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.MSELoss()

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32))
    val_ds = TensorDataset(torch.tensor(X_val, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    print("Training Dense-AE...", flush=True)
    start_time = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for (batch_x,) in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()
            recon = model(batch_x)
            loss = criterion(recon, batch_x)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(batch_x)
        train_loss /= len(X_train)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for (batch_x,) in val_loader:
                batch_x = batch_x.to(device)
                recon = model(batch_x)
                loss = criterion(recon, batch_x)
                val_loss += loss.item() * len(batch_x)
        val_loss /= len(X_val)

        if epoch % 2 == 0 or epoch == epochs:
            print(f"Dense-AE Epoch {epoch:02d}/{epochs} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}", flush=True)

    train_time = time.time() - start_time
    return model, train_time

def train_sequence_ae(ae_class, X_train_seq, X_val_seq, device, model_name="LSTM-AE", epochs=6, batch_size=256, lr=0.001, seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    input_dim = X_train_seq.shape[2]
    model = ae_class(input_dim=input_dim, hidden_dim=64, num_layers=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.MSELoss()

    train_ds = TensorDataset(torch.tensor(X_train_seq, dtype=torch.float32))
    val_ds = TensorDataset(torch.tensor(X_val_seq, dtype=torch.float32))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    print(f"Training {model_name}...", flush=True)
    start_time = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for (batch_x,) in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()
            recon = model(batch_x)
            loss = criterion(recon, batch_x)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(batch_x)
        train_loss /= len(X_train_seq)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for (batch_x,) in val_loader:
                batch_x = batch_x.to(device)
                recon = model(batch_x)
                loss = criterion(recon, batch_x)
                val_loss += loss.item() * len(batch_x)
        val_loss /= len(X_val_seq)

        print(f"{model_name} Epoch {epoch:02d}/{epochs} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}", flush=True)

    train_time = time.time() - start_time
    return model, train_time

def compute_reconstruction_errors_dense(model, X, device, batch_size=1024):
    model.eval()
    ds = TensorDataset(torch.tensor(X, dtype=torch.float32))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False)
    errors = []
    with torch.no_grad():
        for (batch_x,) in loader:
            batch_x = batch_x.to(device)
            recon = model(batch_x)
            err = torch.mean((batch_x - recon)**2, dim=1).cpu().numpy()
            errors.append(err)
    return np.concatenate(errors)

def compute_reconstruction_errors_seq(model, X_seq, device, batch_size=512):
    model.eval()
    ds = TensorDataset(torch.tensor(X_seq, dtype=torch.float32))
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False)
    errors = []
    with torch.no_grad():
        for (batch_x,) in loader:
            batch_x = batch_x.to(device)
            recon = model(batch_x)
            err = torch.mean((batch_x - recon)**2, dim=(1, 2)).cpu().numpy()
            errors.append(err)
    return np.concatenate(errors)

def main():
    print("=" * 60, flush=True)
    print("Starting Baseline Model Training & Anomaly Evaluation", flush=True)
    print("=" * 60, flush=True)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using Compute Device: {device}", flush=True)

    data_path = 'data/processed/ciciot2023_processed.npz'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Processed dataset missing at {data_path}")

    data = np.load(data_path, allow_pickle=True)
    X_train_unsup = data['X_train_unsup']
    X_val_unsup = data['X_val_unsup']
    X_sup_train = data['X_sup_train']
    y_sup_train = data['y_sup_train']
    X_test = data['X_test']
    y_test_binary = data['y_test_binary']
    y_test_subclass = data['y_test_subclass']
    y_test_class = data['y_test_class']

    models_dir = 'data/models'
    metrics_dir = 'results/metrics'
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(metrics_dir, exist_ok=True)

    seq_len = 10
    print(f"Creating sequence windows (sequence length = {seq_len})...", flush=True)
    X_train_seq = create_sequences(X_train_unsup, seq_len=seq_len)
    X_val_seq = create_sequences(X_val_unsup, seq_len=seq_len)
    X_test_seq = create_sequences(X_test, seq_len=seq_len)
    y_test_seq = y_test_binary[seq_len-1:]

    # 1. Dense Autoencoder
    dense_model, dense_t = train_dense_ae(X_train_unsup, X_val_unsup, device, epochs=10)
    torch.save(dense_model.state_dict(), os.path.join(models_dir, 'dense_ae.pt'))
    err_val_dense = compute_reconstruction_errors_dense(dense_model, X_val_unsup, device)
    err_test_dense = compute_reconstruction_errors_dense(dense_model, X_test, device)

    # 2. LSTM Autoencoder
    lstm_model, lstm_t = train_sequence_ae(LSTMAutoencoder, X_train_seq, X_val_seq, device, model_name="LSTM-AE", epochs=6)
    torch.save(lstm_model.state_dict(), os.path.join(models_dir, 'lstm_ae.pt'))
    err_val_lstm = compute_reconstruction_errors_seq(lstm_model, X_val_seq, device)
    err_test_lstm = compute_reconstruction_errors_seq(lstm_model, X_test_seq, device)

    # 3. GRU Autoencoder
    gru_model, gru_t = train_sequence_ae(GRUAutoencoder, X_train_seq, X_val_seq, device, model_name="GRU-AE", epochs=6)
    torch.save(gru_model.state_dict(), os.path.join(models_dir, 'gru_ae.pt'))
    err_val_gru = compute_reconstruction_errors_seq(gru_model, X_val_seq, device)
    err_test_gru = compute_reconstruction_errors_seq(gru_model, X_test_seq, device)

    # 4. Isolation Forest
    iforest = train_isolation_forest(X_train_unsup, random_state=42)
    joblib.dump(iforest, os.path.join(models_dir, 'isolation_forest.pkl'))
    err_val_iforest = evaluate_isolation_forest(iforest, X_val_unsup)
    err_test_iforest = evaluate_isolation_forest(iforest, X_test)

    # 5. XGBoost Supervised Oracle Reference
    xgb_oracle = train_xgboost_oracle(X_sup_train, y_sup_train, random_state=42)
    joblib.dump(xgb_oracle, os.path.join(models_dir, 'xgb_oracle.pkl'))
    probs_test_xgb = predict_xgboost_oracle(xgb_oracle, X_test)

    np.savez_compressed(
        os.path.join(metrics_dir, 'baseline_errors.npz'),
        err_val_dense=err_val_dense,
        err_test_dense=err_test_dense,
        err_val_lstm=err_val_lstm,
        err_test_lstm=err_test_lstm,
        err_val_gru=err_val_gru,
        err_test_gru=err_test_gru,
        err_val_iforest=err_val_iforest,
        err_test_iforest=err_test_iforest,
        probs_test_xgb=probs_test_xgb,
        y_test_binary=y_test_binary,
        y_test_seq=y_test_seq,
        y_test_subclass=y_test_subclass,
        y_test_class=y_test_class
    )

    print("\nAll baseline models trained successfully!", flush=True)
    print(f"Dense-AE Train Time: {dense_t:.2f}s | LSTM-AE Train Time: {lstm_t:.2f}s | GRU-AE Train Time: {gru_t:.2f}s", flush=True)

if __name__ == '__main__':
    main()
