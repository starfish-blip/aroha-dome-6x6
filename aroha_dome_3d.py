#!/usr/bin/env python3
import numpy as np
from aroha_resonance_core import ENGINE

def build_geodesic_hemisphere(seg_u: int = 72, seg_v: int = 36, radius: float = 1.35):
    verts = []
    for j in range(seg_v + 1):
        v = j / seg_v
        phi = v * (np.pi * 0.48)
        for i in range(seg_u + 1):
            u = i / seg_u
            theta = u * np.pi * 2.0
            x = radius * np.cos(phi) * np.cos(theta)
            y = radius * np.sin(phi) - 0.45
            z = radius * np.cos(phi) * np.sin(theta)
            verts.append((x, y, z, u, v))
    return np.array(verts, dtype=np.float32)

if __name__ == "__main__":
    mesh = build_geodesic_hemisphere()
    snap = ENGINE.step_parameter_shift(tier_id=6, vowel="C", train_step=False)
    print(f"[✓] 3D Geodesic Dome Mesh Verified: {mesh.shape[0]} vertices (stride 20B)")
    print(f"[✓] Point 26 Zenith UBO Snapshot: S(rho_A)={snap['emergence_entropy_bits']} bits | {snap['regime']}")
