import sys
import os
import torch

# Add workspace and agent directory to path
sys.path.insert(0, r"/data/quyhv/oil_forecast_tail_risk")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing proposed_extended_sota.py...")
try:
    import proposed_extended_sota
    print("Successfully imported proposed_extended_sota.py")
    
    # Test all SOTA models
    sota_registry = proposed_extended_sota.SOTA_CLASS_REGISTRY
    print(f"Loaded {len(sota_registry)} SOTA models from registry")
    
    for name, model_class in sota_registry.items():
        print(f"Testing {name}...", end=" ")
        try:
            model = model_class(input_dim=10, output_dim=2, horizon=5, seq_len=30)
            x = torch.randn(2, 30, 10)
            out = model(x)
            assert out.shape == (2, 5, 2), f"Expected shape (2, 5, 2), got {out.shape}"
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
except Exception as e:
    print(f"Failed to import/run proposed_extended_sota.py: {e}")
    sys.exit(1)

print("\nTesting proposed_gumnet_family.py...")
try:
    import proposed_gumnet_family
    print("Successfully imported proposed_gumnet_family.py")
    
    # Test all GUMNet variants
    gumnet_registry = proposed_gumnet_family.GUMNET_FAMILY_REGISTRY
    print(f"Loaded {len(gumnet_registry)} GUMNet variants from registry")
    
    for name, model_class in gumnet_registry.items():
        print(f"Testing {name}...", end=" ")
        try:
            # We need to simulate feature_cols matching the index construction in GUMNetHet
            # Let's create dummy feature_cols of size 16
            feature_cols = ['MG97', 'MG95', 'MG92', 'NAPHTHA', 'KERO', 'DO 0.001%', 'DO 0.05%', 'FO 180',
                            'WTI_Daily', 'Brent_EU_Daily', 'BRT_DTD', 'BRT_KH',
                            'USD_Index', 'GPR', 'Ratio_95_WTI', 'Ratio_92_WTI']
            model = model_class(seq_len=30, input_dim=16, output_dim=2, horizon=5, d_feat=64,
                                num_quantiles=3, feature_cols=feature_cols)
            x = torch.randn(2, 30, 16)
            preds, gates = model(x)
            assert preds.shape == (2, 5, 2, 3), f"Expected preds shape (2, 5, 2, 3), got {preds.shape}"
            assert gates.shape == (2, 5, 3), f"Expected gates shape (2, 5, 3), got {gates.shape}"
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

except Exception as e:
    print(f"Failed to import/run proposed_gumnet_family.py: {e}")
    sys.exit(1)

print("\nAll tests completed successfully!")
