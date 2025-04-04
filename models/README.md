# Model Weights and Cache Directory

This directory is used to store downloaded model weights, checkpoints, and cache files. It is excluded from version control via .gitignore.

## Expected Contents

```
models/
├── pixtral/              # Pixtral-12B model weights and cache
├── llama_vision/         # Llama-3.2-11B-Vision model weights and cache
└── doctr/                # DocTR model weights and cache
```

## Note

- This directory is for model weights and cache files ONLY
- Model implementations are located in `src/models/`
- Model configurations are located in `config/models/`
- Large files in this directory are not tracked in git
- Each model should have its own subdirectory
- Keep the directory structure clean and organized

## Supported File Types (ignored in git)

- Model checkpoints (*.ckpt)
- PyTorch model files (*.pt, *.pth)
- Binary model files (*.bin)
- HDF5 files (*.h5)
- Cache directories (.cache/, hub/)
- Hugging Face cache 