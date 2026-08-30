import sys
import os
import unittest
import torch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALL_SOTA_BASELINES, GUM_NET_VARIANTS, get_unified_config
from scripts.train_unified import get_model_instance

class TestModelDispatchAndForward(unittest.TestCase):
    def test_sota_baselines_dispatch(self):
        """Verify that get_model_instance successfully returns functional SOTA baselines."""
        cfg = get_unified_config('XANG', 5)
        # Add dimensions for dispatcher compatibility
        cfg['input_dim'] = 16
        cfg['output_dim'] = 2
        cfg['horizon'] = 5
        cfg['available_features'] = ['feat_abc'] * 16
        cfg['num_quantiles'] = 3

        # We will iterate over all 33 SOTA baselines in ALL_SOTA_BASELINES
        for name in ALL_SOTA_BASELINES:
            with self.subTest(model_name=name):
                try:
                    model = get_model_instance(name, cfg)
                    self.assertIsNotNone(model, f"Model {name} should not be None")
                    
                    # Run forward pass for PyTorch models
                    if hasattr(model, 'forward'):
                        # Batch size=2, seq_len=30, input_dim=16
                        x = torch.randn(2, cfg['seq_len'], 16)
                        out = model(x)
                        self.assertEqual(
                            out.shape, (2, 5, 2),
                            f"Model {name} output shape should be (2, 5, 2), got {out.shape}"
                        )
                except Exception as e:
                    self.fail(f"Failed dispatch or execution for SOTA baseline {name}: {e}")

    def test_gumnet_variants_dispatch(self):
        """Verify that get_model_instance successfully returns functional GUM-Net variants."""
        cfg = get_unified_config('XANG', 5)
        # Add dimensions for dispatcher compatibility
        # List of features used in GUMNetHet to construct index sets
        feature_cols = ['MG97', 'MG95', 'MG92', 'NAPHTHA', 'KERO', 'DO 0.001%', 'DO 0.05%', 'FO 180',
                        'WTI_Daily', 'Brent_EU_Daily', 'BRT_DTD', 'BRT_KH',
                        'USD_Index', 'GPR', 'Ratio_95_WTI', 'Ratio_92_WTI']
        
        cfg['input_dim'] = len(feature_cols)
        cfg['output_dim'] = 2
        cfg['horizon'] = 5
        cfg['available_features'] = feature_cols
        cfg['num_quantiles'] = 3

        for name in GUM_NET_VARIANTS:
            with self.subTest(model_name=name):
                try:
                    model = get_model_instance(name, cfg)
                    self.assertIsNotNone(model, f"Model {name} should not be None")
                    
                    # Run forward pass
                    x = torch.randn(2, cfg['seq_len'], len(feature_cols))
                    preds, gates = model(x)
                    
                    self.assertEqual(
                        preds.shape, (2, 5, 2, 3),
                        f"Model {name} preds shape should be (2, 5, 2, 3), got {preds.shape}"
                    )
                    self.assertEqual(
                        gates.shape, (2, 5, 3),
                        f"Model {name} gates shape should be (2, 5, 3), got {gates.shape}"
                    )
                except Exception as e:
                    self.fail(f"Failed dispatch or execution for GUM-Net variant {name}: {e}")

if __name__ == '__main__':
    unittest.main()
