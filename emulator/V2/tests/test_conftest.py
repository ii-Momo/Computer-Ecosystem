import inspect
import pytest
# We try to adapt to small API differences in the student's emulator implementation.
# Expected package layout: emu.cpu_state, emu.memory, and an executor with a step() function.

def _import_step():
    # Prefer executor_v2, but fall back to other common names.
    candidates = [
        "emu.executor_v2",
        "emu.executor",
        "emu.executor_v1",
    ]
    last_err = None
    for modname in candidates:
        try:
            mod = __import__(modname, fromlist=["step"])
            if hasattr(mod, "step"):
                return mod.step
        except Exception as e:
            last_err = e
    raise ImportError(f"Could not import step() from any executor module {candidates}. Last error: {last_err}")


@pytest.fixture(scope="session")
def step_fn():
    return _import_step()

@pytest.fixture(scope="function")
def state():
    # reset_state should return a state object in most implementations,
    # but if it returns None we will fetch a module-global 'STATE' or 'cpu' as fallback.
    from emu import cpu_state as cs
    st = cs.reset_state()
    if st is not None:
        return st
    for name in ("STATE", "state", "CPU", "cpu"):
        if hasattr(cs, name):
            return getattr(cs, name)
    raise RuntimeError("reset_state() returned None and no known global state object was found in emu.cpu_state")


def run_steps(step_fn, state, mem, max_steps=10_000):
    """
    Step until HALT or FAULT.
    Works with step(mem), step(state, mem), or step(mem, state) call signatures.
    Returns the final state.
    """
    sig = inspect.signature(step_fn)
    params = list(sig.parameters)
    def call_step():
        if len(params) == 1:
            return step_fn(mem)
        if len(params) == 2:
            # Try (state, mem) then (mem, state)
            try:
                return step_fn(state, mem)
            except TypeError:
                return step_fn(mem, state)
        # If more params, try the common (state, mem, ...)
        try:
            return step_fn(state, mem)
        except TypeError:
            return step_fn(mem)

    for _ in range(max_steps):
        res = call_step()
        # If step() returns a halt reason enum, we can use it; otherwise consult state flags.
        if _is_halted_or_faulted(state, res):
            return state
    raise RuntimeError("Program did not halt/fault within max_steps")

def _is_halted_or_faulted(state, step_result=None):
    # Prefer step_result if it looks like an enum with names.
    # Otherwise check common state attributes.
    # We consider the program stopped if HALT or FAULT is reached.
    if step_result is not None:
        name = getattr(step_result, "name", None)
        if name in ("HALT", "HALTED", "FAULT"):
            return True

    for attr in ("halt_reason", "halted", "is_halted"):
        if hasattr(state, attr):
            v = getattr(state, attr)
            if isinstance(v, bool) and v:
                return True
            n = getattr(v, "name", None)
            if n in ("HALT", "HALTED", "FAULT"):
                return True
    # Some implementations keep a "fault_code" that is None when OK
    if getattr(state, "fault_code", None) is not None:
        return True
    return False

def get_fault_code(state):
    # Common fields: fault_code, fault, fault_reason, halt_reason
    for attr in ("fault_code", "fault", "fault_reason", "fault_kind"):
        if hasattr(state, attr):
            v = getattr(state, attr)
            if v is None:
                continue
            return getattr(v, "name", v)
    # Sometimes stored inside halt_reason with additional info
    hr = getattr(state, "halt_reason", None)
    if hr is not None:
        return getattr(hr, "name", hr)
    return None

def get_pc(state):
    for attr in ("pc", "PC"):
        if hasattr(state, attr):
            return int(getattr(state, attr))
    raise AttributeError("Could not find PC field on state (expected state.pc)")

def get_sp(state):
    for attr in ("sp", "SP"):
        if hasattr(state, attr):
            return int(getattr(state, attr))
    raise AttributeError("Could not find SP field on state (expected state.sp)")

def get_fp(state):
    for attr in ("fp", "FP"):
        if hasattr(state, attr):
            return int(getattr(state, attr))
    raise AttributeError("Could not find FP field on state (expected state.fp)")

def set_pc(state, v:int):
    if hasattr(state, "pc"):
        state.pc = int(v)
    elif hasattr(state, "PC"):
        state.PC = int(v)
    else:
        raise AttributeError("Could not set PC on state")

def set_sp(state, v:int):
    if hasattr(state, "sp"):
        state.sp = int(v)
    elif hasattr(state, "SP"):
        state.SP = int(v)
    else:
        raise AttributeError("Could not set SP on state")

def set_fp(state, v:int):
    if hasattr(state, "fp"):
        state.fp = int(v)
    elif hasattr(state, "FP"):
        state.FP = int(v)
    else:
        raise AttributeError("Could not set FP on state")

def get_regs(state):
    # Common: state.regs list, or state.R list, or state.gpr
    for attr in ("regs", "R", "gpr", "registers"):
        if hasattr(state, attr):
            return getattr(state, attr)
    raise AttributeError("Could not find general register file on state (expected state.regs or state.R)")

def reg(state, idx:int):
    return int(get_regs(state)[idx])

def set_reg(state, idx:int, val:int):
    get_regs(state)[idx] = int(val) & ((1<<64)-1)
