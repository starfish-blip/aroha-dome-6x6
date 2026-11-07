#!/usr/bin/env python3
import json
import time
import os
import hashlib
import subprocess
import urllib.request
from dataclasses import dataclass, asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import numpy as np

I2 = np.eye(2, dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=complex)

def rz(theta: float) -> np.ndarray:
    return np.array([
        [np.exp(-1j * theta / 2.0), 0],
        [0, np.exp(1j * theta / 2.0)]
    ], dtype=complex)

def kron_all(matrices: list) -> np.ndarray:
    out = matrices[0]
    for m in matrices[1:]:
        out = np.kron(out, m)
    return out

Z_DIAG = np.array([1.0, -1.0])
RING_PAIRS = [(0, 2), (1, 3), (0, 1), (2, 3)]
ZZ_RING_DIAGS = []
for c_idx, t_idx in RING_PAIRS:
    ops = [np.ones(2) for _ in range(4)]
    ops[c_idx] = Z_DIAG
    ops[t_idx] = Z_DIAG
    diag = ops[0]
    for m in ops[1:]:
        diag = np.kron(diag, m)
    ZZ_RING_DIAGS.append(diag)

CONSCIOUSNESS_TIERS = {
    1: {"name": "Tier 1: Gases (Hau / Atmospheric)", "zone": "Zone 3 (Sub-Elemental)", "temp_c": 24.6, "gamma_scale": 0.05, "lam": 0.05, "inputs": [-0.85, -0.70, -0.60], "targets": [0.20, -0.20, 0.15, -0.15], "disp_gain": 0.08},
    2: {"name": "Tier 2: Liquids (Wai / Fluid Medium)", "zone": "Zone 3 (Elemental)", "temp_c": 28.6, "gamma_scale": 0.30, "lam": 0.15, "inputs": [-0.45, -0.35, 0.10], "targets": [0.40, 0.25, -0.30, 0.35], "disp_gain": 0.12},
    3: {"name": "Tier 3: Plant Life (Stationary Conduit)", "zone": "Zone 3 -> Zone 2 Root", "temp_c": 32.6, "gamma_scale": 0.55, "lam": 0.25, "inputs": [0.15, -0.10, 0.50], "targets": [0.55, 0.50, 0.45, 0.60], "disp_gain": 0.15},
    4: {"name": "Tier 4: Fish & Aquatic (Hydrodynamic)", "zone": "Zone 2 (Spiral Bridge)", "temp_c": 34.6, "gamma_scale": 0.85, "lam": 0.35, "inputs": [0.35, 0.20, 0.40], "targets": [0.65, 0.60, 0.70, 0.65], "disp_gain": 0.18},
    5: {"name": "Tier 5: Mammals (36.6C Homeostasis)", "zone": "Zone 2 (Biological Fulcrum)", "temp_c": 36.6, "gamma_scale": 1.25, "lam": 0.50, "inputs": [0.55, 0.45, 0.60], "targets": [0.75, 0.75, 0.80, 0.75], "disp_gain": 0.22},
    6: {"name": "Tier 6: Sentient Observer (Point 26 Zenith)", "zone": "Zone 1 (Cosmic Dome)", "temp_c": 38.1, "gamma_scale": 1.85, "lam": 0.75, "inputs": [0.80, 0.70, 0.85], "targets": [0.88, 0.85, 0.90, 0.92], "disp_gain": 0.28}
}

VOWEL_MAP = {
    "C": {"role": "36.6C Vocal Baseline Anchor (261.63 Hz)", "f1": 500.0, "f2": 1500.0, "phase_bias": 0.00},
    "A": {"role": "Spark / Heart-Chest Origin (432 Hz)",     "f1": 730.0, "f2": 1090.0, "phase_bias": 0.18},
    "E": {"role": "Bridge / Throat Gateway (639 Hz)",        "f1": 530.0, "f2": 1840.0, "phase_bias": 0.38},
    "I": {"role": "Observer / Crown Handshake (741 Hz)",     "f1": 270.0, "f2": 2290.0, "phase_bias": 0.70},
    "O": {"role": "Pour / Torus Equator (417 Hz)",           "f1": 570.0, "f2": 840.0,  "phase_bias": -0.35},
    "U": {"role": "Mold / Core Terra Lattice (396 Hz)",      "f1": 300.0, "f2": 870.0,  "phase_bias": -0.70}
}

LADDER_MAP = {
    3: {"label": "Level 3: Obsidian / Iron (Fe) / Infra-Red", "octave_mult": 0.5, "element": "Iron (Fe) / Obsidian"},
    6: {"label": "Level 6: Pounamu / Copper (Cu) / Vocal Green", "octave_mult": 1.0, "element": "Copper (Cu) / Pounamu"},
    9: {"label": "Level 9: Citrine-Lapis / Gold (Au) / Violet-Gold", "octave_mult": 2.0, "element": "Gold (Au) / Citrine"}
}

MODE_NAMES = ["Thermal (Mode 0)", "Agent (Mode 1)", "Constraint (Mode 2)", "Resource (Mode 3)"]

@dataclass
class ThermalEncoding:
    raw_temp_c: float
    delta_t: float
    freq_hz: float
    phase_rad: float

class ArohaResonanceEngine:
    def __init__(self, learning_rate: float = 0.12):
        self.n_modes = 4
        self.lr = learning_rate
        self.start_time = time.time()
        self.empirical_validity = 0.5
        self.ledger_file = "aroha_ledger.json"
        self.reset_weights()
        self.observables = []
        for k in range(self.n_modes):
            ops = [I2] * self.n_modes
            ops[k] = Z
            self.observables.append(kron_all(ops))

    def reset_weights(self):
        rng = np.random.default_rng(42)
        self.W = rng.uniform(-0.45, 0.45, size=(self.n_modes, 3))
        self.W[:, 2] = 0.65

    @staticmethod
    def encode_thermal(temp_c: float) -> ThermalEncoding:
        delta_t = temp_c - 36.6
        freq_hz = 261.63 * (2.0 ** (delta_t / 12.0))
        phase_rad = float(np.clip((np.pi * delta_t) / 12.0, -np.pi, np.pi))
        return ThermalEncoding(round(float(temp_c), 3), round(float(delta_t), 3), round(float(freq_hz), 3), round(phase_rad, 4))

    def prepare_input_state(self, temp_c: float, inputs: list, vowel_bias: float, lunar_bias: float) -> np.ndarray:
        therm = self.encode_thermal(temp_c)
        angles = [
            therm.phase_rad + vowel_bias * 0.5 + lunar_bias,
            float(np.clip(inputs[0] + vowel_bias * 0.3, -1.0, 1.0)) * (np.pi / 2.0),
            float(np.clip(inputs[1] - vowel_bias * 0.3, -1.0, 1.0)) * (np.pi / 2.0),
            float(np.clip(inputs[2] + lunar_bias, -1.0, 1.0)) * (np.pi / 2.0)
        ]
        psi_0 = np.zeros(2 ** self.n_modes, dtype=complex)
        psi_0[0] = 1.0
        return kron_all([ry(a) for a in angles]) @ psi_0

    def forward(self, psi_t: np.ndarray, W: np.ndarray = None, gamma_scale: float = 1.0):
        if W is None:
            W = self.W
        psi_1 = kron_all([ry(W[k, 0]) for k in range(self.n_modes)]) @ psi_t
        total_phase = np.zeros(16, dtype=float)
        for idx in range(self.n_modes):
            total_phase += (W[idx, 2] * gamma_scale / 2.0) * ZZ_RING_DIAGS[idx]
        psi_2 = np.exp(-1j * total_phase) * psi_1
        psi_next = kron_all([rz(W[k, 1]) @ ry(W[k, 1]) for k in range(self.n_modes)]) @ psi_2
        y_vec = np.array([np.real(np.vdot(psi_next, M_k @ psi_next)) for M_k in self.observables])
        return psi_next, y_vec

    @staticmethod
    def emergence_entropy(psi: np.ndarray) -> float:
        psi_mat = psi.reshape(4, 4)
        rho_A = psi_mat @ psi_mat.conj().T
        eigenvals = np.linalg.eigvalsh(rho_A)
        eigenvals = eigenvals[eigenvals > 1e-12]
        return float(-np.sum(eigenvals * np.log2(eigenvals)))

    def compute_loss(self, psi_t: np.ndarray, W: np.ndarray, y_target: np.ndarray, lam: float, gamma_scale: float):
        psi_next, y_vec = self.forward(psi_t, W, gamma_scale)
        s_ab = self.emergence_entropy(psi_next)
        mse = float(np.mean((y_vec - y_target) ** 2))
        loss = mse - (lam * max(0.2, self.empirical_validity) * s_ab)
        return loss, psi_next, y_vec, s_ab

    def get_ledger(self) -> list:
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def append_tier3_ledger(self, record: dict) -> str:
        chain = self.get_ledger()
        prev_hash = chain[-1]["sha256"] if chain else "0" * 64
        payload_str = json.dumps(record, sort_keys=True) + prev_hash
        digest = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        entry = {
            "index": len(chain) + 1,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "prev_hash": prev_hash,
            "sha256": digest,
            "state": record
        }
        chain.append(entry)
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(chain, f, indent=2)
        return digest[:16]

    def step_parameter_shift(self, tier_id: int = 6, temp_c: float = 38.1, gamma_scale: float = 1.85, lam: float = 0.75, vowel: str = "A", ladder_level: int = 9, maramataka: str = "Rakaunui", train_step: bool = True) -> dict:
        tier = CONSCIOUSNESS_TIERS.get(tier_id, CONSCIOUSNESS_TIERS[6])
        v_info = VOWEL_MAP.get(vowel.upper(), VOWEL_MAP["A"])
        l_info = LADDER_MAP.get(ladder_level, LADDER_MAP[9])
        lunar_bias = 0.22 if maramataka == "Rakaunui" else -0.22
        y_target = np.array(tier["targets"], dtype=float)
        therm = self.encode_thermal(temp_c)
        psi_t = self.prepare_input_state(temp_c, tier["inputs"], v_info["phase_bias"], lunar_bias)
        grad = np.zeros_like(self.W)
        shift = np.pi / 2.0
        if train_step:
            for k in range(self.n_modes):
                for j in range(3):
                    W_plus, W_minus = self.W.copy(), self.W.copy()
                    W_plus[k, j] += shift
                    W_minus[k, j] -= shift
                    l_plus, _, _, _ = self.compute_loss(psi_t, W_plus, y_target, lam, gamma_scale)
                    l_minus, _, _, _ = self.compute_loss(psi_t, W_minus, y_target, lam, gamma_scale)
                    grad[k, j] = 0.5 * (l_plus - l_minus)
            self.W = np.clip(self.W - self.lr * grad, -np.pi, np.pi)
        loss, psi_next, y_vec, s_ab = self.compute_loss(psi_t, self.W, y_target, lam, gamma_scale)
        return {
            "y_vector": [round(float(x), 4) for x in y_vec],
            "thermal": asdict(therm),
            "emergence_entropy_bits": round(s_ab, 5),
            "empirical_validity": round(float(self.empirical_validity), 2),
            "loss": round(float(loss), 5),
            "time_sec": round(time.time() - self.start_time, 3),
            "weights": [[round(float(val), 4) for val in row] for row in self.W],
            "grad_norm": round(float(np.linalg.norm(grad)), 5),
            "regime": "1+1=3 (Emergent)" if s_ab > 0.05 else "1+1=2 (Separable)",
            "tier": {"id": tier_id, "name": tier["name"], "zone": tier["zone"], "disp_gain": tier["disp_gain"]},
            "vowel": {"char": vowel.upper(), "role": v_info["role"], "f1": v_info["f1"], "f2": v_info["f2"]},
            "ladder": {"level": ladder_level, "label": l_info["label"], "octave_mult": l_info["octave_mult"], "element": l_info["element"]},
            "maramataka": maramataka
        }

    def handle_oracle_reflection(self, payload: dict) -> dict:
        prompt = str(payload.get("prompt", "Decode current state")).strip()
        snap = self.step_parameter_shift(
            tier_id=int(payload.get("tier_id", 6)),
            temp_c=float(payload.get("temp_c", 38.1)),
            gamma_scale=float(payload.get("gamma_scale", 1.85)),
            lam=float(payload.get("lam", 0.75)),
            vowel=str(payload.get("vowel", "A")),
            ladder_level=int(payload.get("ladder_level", 9)),
            maramataka=str(payload.get("maramataka", "Rakaunui")),
            train_step=False
        )
        carrier_hz = round(snap["thermal"]["freq_hz"] * snap["ladder"]["octave_mult"], 2)
        y_vec = snap["y_vector"]
        dom_idx = int(np.argmax(np.abs(y_vec)))
        dom_mode = MODE_NAMES[dom_idx]
        dom_val = y_vec[dom_idx]
        dt = snap["thermal"]["delta_t"]
        thermal_note = "locked at the 36.6Â°C biological superconductor baseline" if abs(dt) < 0.05 else f"running {dt:+.1f}Â°C from the 36.6Â°C fulcrum"
        synth_reply = (
            f"[{snap['tier']['name']} | {snap['ladder']['element']} | {snap['maramataka']}] "
            f"Regarding \"{prompt}\": Field is {thermal_note} at {carrier_hz} Hz, "
            f"with Vocal Key '{snap['vowel']['char']}' ({snap['vowel']['role']}) driving {dom_mode} ({dom_val:+.3f}). "
            f"Cross-partition entanglement is S(Ï_A) = {snap['emergence_entropy_bits']:.4f} bits [{snap['regime']}]."
        )
        return {
            "reply": synth_reply,
            "source": "Python Quantum State Synthesizer",
            "telemetry_badge": f"{snap['tier']['name'].split(':')[0]} | Key {snap['vowel']['char']} | {carrier_hz}Hz | S={snap['emergence_entropy_bits']:.3f}b"
        }

ENGINE = ArohaResonanceEngine()

class ArohaRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/ledger":
            chain = ENGINE.get_ledger()
            body = json.dumps({"count": len(chain), "entries": chain[-5:]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        payload = json.loads(raw_body) if raw_body else {}

        if self.path == "/api/reset":
            ENGINE.reset_weights()
            ENGINE.empirical_validity = 0.5
            res = ENGINE.step_parameter_shift(train_step=False)
        elif self.path == "/api/tarot/handshake":
            try:
                rec = payload.get("entry", payload)
                rec["type"] = "tarot"
                rec["origin"] = "tarot_v1.1"
                h = ENGINE.append_tier3_ledger(rec)
                res = {"status": "TAROT COMMITTED", "hash": h}
            except Exception as e:
                res = {"error": str(e)}
        elif self.path == "/api/handshake":
            action = payload.get("action", "confirm")
            if action == "confirm":
                ENGINE.empirical_validity = 1.0
                snap = ENGINE.step_parameter_shift(train_step=False)
                if "entry" in payload:
                    snap["attached_entry"] = payload["entry"]
                short_hash = ENGINE.append_tier3_ledger(snap)
                res = {"status": "CONFIRMED (1+1=3 Gold Lock)", "validity": 1.0, "hash": short_hash}
            else:
                ENGINE.empirical_validity = 0.0
                ENGINE.reset_weights()
                res = {"status": "REJECTED (3-1=1 Magenta Reset)", "validity": 0.0, "hash": "RESET"}
        elif self.path == "/api/oracle":
            res = ENGINE.handle_oracle_reflection(payload)
        else:
            res = ENGINE.step_parameter_shift(
                tier_id=int(payload.get("tier_id", 6)),
                temp_c=float(payload.get("temp_c", 38.1)),
                gamma_scale=float(payload.get("gamma_scale", 1.85)),
                lam=float(payload.get("lam", 0.75)),
                vowel=str(payload.get("vowel", "A")),
                ladder_level=int(payload.get("ladder_level", 9)),
                maramataka=str(payload.get("maramataka", "Rakaunui")),
                train_step=bool(payload.get("train_step", True))
            )

        body = json.dumps(res).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("=== AROHA v40 Master Matrix + Tarot/Astro/Domains Bridge Online ===")
    print("Listening on http://localhost:8080/aroha_master_matrix_app.html")
    server = ThreadingHTTPServer(("0.0.0.0", 8080), ArohaRequestHandler)
    server.serve_forever()




