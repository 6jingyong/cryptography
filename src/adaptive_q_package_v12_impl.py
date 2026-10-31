# Adaptive package
# ---------------------------------------------------------------------------

TABLE_BLUEPRINT = [
    ("affine",     0.0045),
    ("affine",     0.0150),
    ("affine",     0.0350),
    ("periodic",   0.0045),
    ("periodic",   0.0150),
    ("periodic",   0.0350),
    ("saturation", 0.0045),
    ("saturation", 0.0150),
    ("saturation", 0.0350),
    ("gaussian",   0.0045),
    ("gaussian",   0.0150),
    ("gaussian",   0.0350),
]


def split_bits(total_bits: np.ndarray, tables: int):
    n = len(total_bits)
    starts = [round(i*n/tables) for i in range(tables+1)]
    return [total_bits[starts[i]:starts[i+1]] for i in range(tables)]


def encode_table(bit_chunk: np.ndarray, table_id: int, family: str, chosen: dict, channels: int):
    q = chosen["q"]
    m = Q_MODES[q]["m"]
    spec = family_spec(family)
    n = spec.protected_dims + q + 1
    x = local_x(n)
    B = basis_for(spec, x)
    U = smooth_free_basis(B)

    payload_syms, bit_length = bits_to_symbols(bit_chunk, m)
    syms_per_cw = q - 2
    blocks = math.ceil(len(payload_syms) / syms_per_cw)
    padded = np.pad(payload_syms, (0, blocks*syms_per_cw-len(payload_syms)))
    payload = padded.reshape(blocks, syms_per_cw)

    cw = choose_codewords(payload, q, U, chosen["delta"])

    segments = math.ceil(blocks / channels)
    slots = segments * channels
    padded_cw = np.zeros((slots, q+1), dtype=np.uint16)
    padded_cw[:blocks] = cw

    baselines_z = []
    baselines_y = []
    for c in range(channels):
        _, _, _, z0, y0 = baseline(spec, q, c, channels)
        baselines_z.append(z0)
        baselines_y.append(y0)
    baselines_z = np.asarray(baselines_z)
    baselines_y = np.asarray(baselines_y)

    channel_ids = np.arange(slots) % channels
    coeff = LEVEL_CACHE[q][padded_cw] * chosen["delta"]
    z = baselines_z[channel_ids] + coeff @ U.T
    y = inverse_y(z, spec.transform)
    if chosen["publication_model"] == "log_step":
        zp = np.round(z / chosen["publication_step"]) * chosen["publication_step"]
        yp = inverse_y(zp, spec.transform)
    else:
        yp = np.round(y / chosen["publication_step"]) * chosen["publication_step"]

    # reshape ordinary multivariate table: rows = segments*n, cols = channels
    pub = np.empty((segments*n, channels), dtype=np.float64)
    for s in range(segments):
        row0 = s*n
        pub[row0:row0+n, :] = yp[s*channels:(s+1)*channels].T

    manifest = {
        "table_id": table_id,
        "family": family,
        "transform": spec.transform,
        "q": q,
        "m": m,
        "poly": Q_MODES[q]["poly"],
        "channels": channels,
        "points_per_block": n,
        "segments": segments,
        "valid_codewords": blocks,
        "payload_bit_length": bit_length,
        "publication_step": chosen["publication_step"],
        "publication_model": chosen["publication_model"],
        "delta": chosen["delta"],
        "residual_budget_nrmse": chosen["budget_nrmse"],
        "calibration_nrmse": chosen["nrmse"],
        "calibration_bits_per_value": chosen["bits_per_value"],
    }
    return x, pub, manifest


def decode_table(pub: np.ndarray, manifest: dict):
    family = manifest["family"]
    q = int(manifest["q"])
    m = int(manifest["m"])
    channels = int(manifest["channels"])
    n = int(manifest["points_per_block"])
    segments = int(manifest["segments"])
    valid = int(manifest["valid_codewords"])
    delta = float(manifest["delta"])

    spec = family_spec(family)
    x = local_x(n)
    B = basis_for(spec, x)
    U = smooth_free_basis(B)

    recovered = np.empty((segments*channels, q-2), dtype=np.uint16)
    k = 0
    for s in range(segments):
        Y = pub[s*n:(s+1)*n, :].T
        Z = transform_y(Y, spec.transform)
        pinv = np.linalg.pinv(B)
        beta = Z @ pinv.T
        fit = beta @ B.T
        raw = nearest_symbols((Z-fit) @ U, q, delta)
        corr = hamming_correct(raw, q)
        recovered[k:k+channels] = corr[:, :q-2]
        k += channels

    recovered = recovered[:valid].reshape(-1)
    return symbols_to_bits(recovered, m, int(manifest["payload_bit_length"]))


def run_package(payload_bytes: int = 131072, channels: int = 16, out_dir: Path = Path("v12_out")):
    out_dir.mkdir(parents=True, exist_ok=True)

    # Calibrate/select q table by table.
    selected = []
    calibrations = []
    for i, (family, budget) in enumerate(TABLE_BLUEPRINT):
        chosen, trials = choose_q_for_table(family, budget, channels)
        chosen = dict(chosen)
        chosen["budget_nrmse"] = budget
        selected.append((family, chosen))
        calibrations.append({"table_id": i, "family": family, "budget": budget, "trials": trials, "chosen_q": chosen["q"]})

    payload = synthetic_payload(payload_bytes)
    bits = bytes_to_bits(payload)
    chunks = split_bits(bits, len(selected))

    arrays = {}
    table_manifests = []
    bit_cursor = 0

    for i, ((family, chosen), chunk) in enumerate(zip(selected, chunks)):
        x, pub, tm = encode_table(chunk, i, family, chosen, channels)
        tm["payload_bit_offset"] = bit_cursor
        bit_cursor += len(chunk)
        arrays[f"table_{i}_x"] = x
        arrays[f"table_{i}_y"] = pub
        table_manifests.append(tm)

    package_path = out_dir / "published_adaptive_q_v12.npz"
    np.savez_compressed(package_path, **arrays)

    manifest = {
        "version": "adaptive-q-v12",
        "scope": "synthetic-only",
        "payload_bytes": payload_bytes,
        "payload_bit_length": len(bits),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "q_candidates": [8, 16, 32],
        "tables": table_manifests,
    }
    manifest_path = out_dir / "manifest_adaptive_q_v12.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Decode ONLY from package + manifest.
    loaded = np.load(package_path)
    recovered_bits = np.zeros(len(bits), dtype=np.uint8)
    for tm in table_manifests:
        i = tm["table_id"]
        rb = decode_table(loaded[f"table_{i}_y"], tm)
        off = int(tm["payload_bit_offset"])
        recovered_bits[off:off+len(rb)] = rb

    recovered = bits_to_bytes(recovered_bits)[:payload_bytes]

    manifest_bytes = len(manifest_path.read_bytes())
    total_rows = sum(arrays[f"table_{i}_y"].shape[0] for i in range(len(selected)))
    total_values = total_rows * channels
    q_counts = {str(q): sum(1 for _, c in selected if c["q"] == q) for q in (8,16,32)}

    result = {
        "version": "adaptive-q-v12",
        "scope": "synthetic-only",
        "payload_bytes": payload_bytes,
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "decoded_sha256": hashlib.sha256(recovered).hexdigest(),
        "exact_recovery": recovered == payload,
        "channels_per_table": channels,
        "table_count": len(selected),
        "q_distribution": q_counts,
        "manifest_bytes": manifest_bytes,
        "manifest_overhead_percent": 100.0 * manifest_bytes / payload_bytes,
        "published_rows_total": total_rows,
        "published_numeric_values_total": total_values,
        "gross_bits_per_row": payload_bytes*8 / total_rows,
        "net_bits_per_row_after_manifest": (payload_bytes*8 - manifest_bytes*8) / total_rows,
        "gross_bits_per_numeric_value": payload_bytes*8 / total_values,
        "selected_tables": [
            {
                "table_id": i,
                "family": family,
                "budget_nrmse": chosen["budget_nrmse"],
                "q": chosen["q"],
                "calibration_nrmse": chosen["nrmse"],
                "calibration_roughness_ratio": chosen["roughness_ratio"],
                "calibration_raw_ser": chosen["raw_ser"],
                "calibration_multi_symbol_error_blocks": chosen["multi_symbol_error_blocks"],
                "publication_model": chosen["publication_model"],
                "calibration_bits_per_value": chosen["bits_per_value"],
            }
            for i, (family, chosen) in enumerate(selected)
        ],
        "calibrations": calibrations,
    }
    (out_dir / "adaptive_q_v12_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload-bytes", type=int, default=131072)
    ap.add_argument("--channels", type=int, default=16)
    ap.add_argument("--out-dir", type=Path, default=Path("v12_out"))
    args = ap.parse_args()
    result = run_package(args.payload_bytes, args.channels, args.out_dir)
    slim = {k:v for k,v in result.items() if k != "calibrations"}
    print(json.dumps(slim, indent=2))


if __name__ == "__main__":
    main()
