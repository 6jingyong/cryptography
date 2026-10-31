

def channel_beta(spec: FamilySpec, channel: int, channels: int) -> np.ndarray:
    phase = 2.0 * np.pi * channel / max(channels, 1)

    if spec.family == "affine":
        return np.asarray([50.0 + 0.25*channel, 8.0 + 0.7*np.sin(phase)])

    if spec.family == "periodic":
        # basis: DC, sin w, cos w, sin 2w, cos 2w
        return np.asarray([
            55.0 + 0.20*channel,
            7.0 + 0.6*np.sin(phase),
            1.6*np.cos(0.3*phase),
            1.4 + 0.3*np.cos(phase),
            0.5*np.sin(phase),
        ])

    if spec.family == "saturation":
        # y = A + C exp(-t/tau), with C negative for rising saturation.
        return np.asarray([58.0 + 0.2*channel, -(24.0 + 1.2*np.sin(phase))])

    if spec.family == "gaussian":
        # log y = a + b x + c x^2, c<0
        mu = 0.10*np.sin(phase)
        sigma = 0.55 + 0.03*np.cos(phase)
        amp = 45.0 + 1.5*np.sin(phase)
        c = -1.0/(2*sigma*sigma)
        b = mu/(sigma*sigma)
        a = math.log(amp) - mu*mu/(2*sigma*sigma)
        return np.asarray([a, b, c])

    raise ValueError(spec.family)


def transform_y(y: np.ndarray, transform: str) -> np.ndarray:
    if transform == "identity":
        return np.asarray(y, dtype=np.float64)
    if transform == "log":
        return np.log(np.asarray(y, dtype=np.float64))
    raise ValueError(transform)


def inverse_y(z: np.ndarray, transform: str) -> np.ndarray:
    if transform == "identity":
        return np.asarray(z, dtype=np.float64)
    if transform == "log":
        return np.exp(np.asarray(z, dtype=np.float64))
    raise ValueError(transform)


def baseline(spec: FamilySpec, q: int, channel: int, channels: int):
    n = spec.protected_dims + q + 1
    x = local_x(n)
    B = basis_for(spec, x)
    beta = channel_beta(spec, channel, channels)
    z = B @ beta
    y = inverse_y(z, spec.transform)
    return x, B, beta, z, y


def second_difference_matrix(n: int):
    D = np.zeros((n-2, n), dtype=np.float64)
    for i in range(n-2):
        D[i, i:i+3] = (1.0, -2.0, 1.0)
    return D


def smooth_free_basis(B: np.ndarray):
    Q, _ = np.linalg.qr(B, mode="complete")
    rank = int(np.linalg.matrix_rank(B))
    U0 = Q[:, rank:]
    D2 = second_difference_matrix(B.shape[0])
    G = (D2 @ U0).T @ (D2 @ U0)
    vals, V = np.linalg.eigh(G)
    U = U0 @ V[:, np.argsort(vals)]
    for j in range(U.shape[1]):
        k = int(np.argmax(np.abs(U[:, j])))
        if U[k, j] < 0:
            U[:, j] *= -1
    return U


# ---------------------------------------------------------------------------
# Shaping and one-table codec
# ---------------------------------------------------------------------------

def shaping_matrix(U: np.ndarray):
    D2 = second_difference_matrix(U.shape[0])
    return U.T @ U + 0.25 * (D2 @ U).T @ (D2 @ U)


def choose_codewords(payload_syms: np.ndarray, q: int, U: np.ndarray, delta: float):
    """
    One shaping symbol. payload_syms shape (blocks, q-2).
    """
    nblocks = len(payload_syms)
    M = shaping_matrix(U)
    levels = LEVEL_CACHE[q]

    best_cost = np.full(nblocks, np.inf)
    best = np.empty((nblocks, q+1), dtype=np.uint16)

    for shape in range(q):
        info = np.empty((nblocks, q-1), dtype=np.uint16)
        info[:, :q-2] = payload_syms
        info[:, q-2] = shape
        cw = hamming_encode(info, q)
        coeff = levels[cw] * delta
        cost = np.einsum("bi,ij,bj->b", coeff, M, coeff, optimize=True)
        take = cost < best_cost
        best_cost[take] = cost[take]
        best[take] = cw[take]
    return best


def nearest_symbols(coeff: np.ndarray, q: int, delta: float):
    idx = np.rint(coeff / delta + (q - 1) / 2).astype(np.int64)
    return np.clip(idx, 0, q-1).astype(np.uint16)


def nrmse(reference: np.ndarray, test: np.ndarray):
    denom = float(np.ptp(reference))
    if denom <= 1e-15:
        denom = float(np.std(reference)) or 1.0
    return float(np.sqrt(np.mean((test-reference)**2)) / denom)


def calibrate(family: str, q: int, budget: float, channels: int, blocks: int = 4096):
    spec = family_spec(family)
    x, B, _, _, y0 = baseline(spec, q, 0, channels)
    U = smooth_free_basis(B)
    assert U.shape[1] == q + 1

    # Publication precision model is transform-aware.
    Y0 = np.asarray([baseline(spec, q, c, channels)[4] for c in range(channels)])
    global_range = float(np.max(Y0) - np.min(Y0))
    if spec.transform == "log":
        # Relative/significant-digit-like publication: fixed step in log(y).
        publication_model = "log_step"
        pub_step = math.log1p(1e-3)
        delta = pub_step * float(Q_MODES[q]["delta_multiple"])
    else:
        publication_model = "absolute_step"
        pub_step = global_range * 1e-3
        delta = pub_step * float(Q_MODES[q]["delta_multiple"])

    rng = np.random.default_rng(12000 + q*17 + sum(map(ord, family)))
    payload = rng.integers(0, q, size=(blocks, q-2), dtype=np.uint16)
    cw = choose_codewords(payload, q, U, delta)

    z0 = transform_y(y0, spec.transform)
    z = z0[None, :] + (LEVEL_CACHE[q][cw] * delta) @ U.T
    y = inverse_y(z, spec.transform)
    if publication_model == "log_step":
        zp = np.round(z / pub_step) * pub_step
        yp = inverse_y(zp, spec.transform)
    else:
        yp = np.round(y / pub_step) * pub_step
        zp = transform_y(yp, spec.transform)
    pinv = np.linalg.pinv(B)
    beta = zp @ pinv.T
    fit = beta @ B.T
    raw = nearest_symbols((zp-fit) @ U, q, delta)
    corrected = hamming_correct(raw, q)

    exact = float(np.mean(np.all(corrected[:, :q-2] == payload, axis=1)))
    err = float(np.mean([nrmse(y0, yy) for yy in yp]))
    base_r = float(np.sum(np.diff(y0, n=2)**2))
    rough = float(np.mean(np.sum(np.diff(yp, n=2, axis=1)**2, axis=1)) / max(base_r, 1e-15))
    symbol_errors_per_block = np.sum(raw != cw, axis=1)
    ser = float(np.mean(raw != cw))
    multi_symbol_error_blocks = int(np.sum(symbol_errors_per_block > 1))
    min_symbol_margin = float(np.min(
        np.abs((zp-fit) @ U / delta - (raw.astype(np.float64) - (q-1)/2))
    ))

    return {
        "family": family,
        "q": q,
        "budget_nrmse": budget,
        "exact_block_recovery": exact,
        "nrmse": err,
        "roughness_ratio": rough,
        "raw_ser": ser,
        "multi_symbol_error_blocks": multi_symbol_error_blocks,
        "min_symbol_margin_to_decision": min_symbol_margin,
        "publication_step": pub_step,
        "publication_model": publication_model,
        "delta": delta,
        "points_per_block": len(x),
        "bits_per_value": (q-2) * Q_MODES[q]["m"] / len(x),
        "feasible": (
            exact == 1.0
            and multi_symbol_error_blocks == 0
            and err <= budget
        ),
    }


def choose_q_for_table(family: str, budget: float, channels: int):
    trials = []
    for q in (8, 16, 32):
        r = calibrate(family, q, budget, channels)
        trials.append(r)
    feasible = [r for r in trials if r["feasible"]]
    if not feasible:
        # Do not silently declare an infeasible carrier safe. Use the lowest-q
        # candidate only as an explicit failure/fallback marker.
        chosen = min(trials, key=lambda r: (r["nrmse"], r["q"]))
        chosen = dict(chosen)
        chosen["fallback_infeasible"] = True
    else:
        chosen = max(feasible, key=lambda r: r["q"])
        chosen = dict(chosen)
        chosen["fallback_infeasible"] = False
    return chosen, trials


# ---------------------------------------------------------------------------
