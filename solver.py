from collections import deque
import math
import heapq


def solve(target, extractable, operations_enabled, max_steps=200):
    if target <= 0:
        return None, "Target must be positive"
    if target in extractable:
        return [{"op": "extract", "value": target}], None

    extractable = sorted(set(extractable))
    ops = set(operations_enabled)

    path = _solve_smart(target, extractable, ops)
    if path:
        return path, None

    path = _solve_bfs(target, extractable, ops, max_steps=max_steps)
    if path:
        return path, None

    error = _build_error_message(target, extractable, ops)
    return None, error


def _solve_smart(target, extractable, ops):
    if '+' in ops and '*' in ops:
        path = _solve_add_mul(target, extractable)
        if path:
            return path

    if '+' in ops:
        path = _solve_addition_only(target, extractable)
        if path:
            return path

    if '*' in ops:
        path = _solve_multiplication_only(target, extractable)
        if path:
            return path

    if '+' in ops and '^' in ops:
        path = _solve_add_exp(target, extractable)
        if path:
            return path

    if '*' in ops and '^' in ops:
        path = _solve_mul_exp(target, extractable)
        if path:
            return path

    if '^' in ops:
        path = _solve_exp_only(target, extractable)
        if path:
            return path

    return None


def _solve_addition_only(target, extractable):
    if not extractable:
        return None
    if target in extractable:
        return [{"op": "extract", "value": target}]

    path = []
    remaining = target
    sorted_ext = sorted(extractable, reverse=True)

    while remaining > 0:
        if remaining in extractable:
            path.append({"op": "extract", "value": remaining})
            break
        used = False
        for e in sorted_ext:
            if e <= remaining:
                if not path:
                    path.append({"op": "extract", "value": e})
                    remaining -= e
                else:
                    last_val = path[-1].get("result", path[-1].get("value", 0))
                    new_val = last_val + e
                    path.append({"op": "+", "a": last_val, "b": e, "result": new_val})
                    remaining -= e
                used = True
                break
        if not used:
            break

    if remaining == 0 and path:
        return path
    return None


def _solve_add_mul(target, extractable):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    best = None
    best_len = float('inf')

    for base in sorted(extractable):
        if base <= 1:
            continue
        if target % base == 0:
            quotient = target // base
            sub = _solve_addition_only(quotient, extractable)
            if sub:
                path = list(sub)
                last_val = path[-1].get("result", path[-1].get("value", 0))
                path.append({"op": "*", "a": last_val, "b": base, "result": last_val * base})
                if len(path) < best_len:
                    best_len = len(path)
                    best = path

    for base in sorted(extractable):
        if base <= 1:
            continue
        quotient = target // base
        remainder = target % base
        if quotient > 0:
            sub_path = _solve_addition_only(quotient, extractable)
            if sub_path:
                path = list(sub_path)
                last_val = path[-1].get("result", path[-1].get("value", 0))
                path.append({"op": "*", "a": last_val, "b": base, "result": last_val * base})
                if remainder > 0:
                    if remainder in extractable:
                        last_val = path[-1]["result"]
                        path.append({"op": "+", "a": last_val, "b": remainder, "result": last_val + remainder})
                    else:
                        continue
                if len(path) < best_len:
                    best_len = len(path)
                    best = path

    for e1 in sorted(extractable):
        for e2 in sorted(extractable):
            if e1 * e2 <= target:
                prod = e1 * e2
                diff = target - prod
                if diff == 0:
                    path = [
                        {"op": "extract", "value": e1},
                        {"op": "*", "a": e1, "b": e2, "result": prod}
                    ]
                    if len(path) < best_len:
                        best_len = len(path)
                        best = path
                elif diff in extractable:
                    path = [
                        {"op": "extract", "value": e1},
                        {"op": "*", "a": e1, "b": e2, "result": prod},
                        {"op": "+", "a": prod, "b": diff, "result": target}
                    ]
                    if len(path) < best_len:
                        best_len = len(path)
                        best = path

    if best:
        return best
    return None


def _solve_multiplication_only(target, extractable):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    factors = _get_factorizations(target, extractable)
    if factors:
        return factors
    return None


def _get_factorizations(target, extractable):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    for e in sorted(extractable, reverse=True):
        if e > 1 and target % e == 0:
            sub = _get_factorizations(target // e, extractable)
            if sub:
                last_val = sub[-1].get("result", sub[-1].get("value", 0))
                sub.append({"op": "*", "a": last_val, "b": e, "result": last_val * e})
                return sub
    return None


def _solve_add_exp(target, extractable):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    for base in sorted(extractable):
        if base <= 1:
            continue
        for exp in range(2, 20):
            try:
                power = base ** exp
                if power > target:
                    break
                if power == target:
                    path = [
                        {"op": "extract", "value": base},
                    ]
                    for _ in range(exp - 1):
                        last_val = path[-1].get("result", path[-1].get("value", 0))
                        path.append({"op": "*", "a": last_val, "b": base, "result": last_val * base})
                    return path
                diff = target - power
                if diff > 0:
                    add_path = _solve_addition_only(diff, extractable)
                    if add_path:
                        path = list(add_path)
                        last_val = path[-1].get("result", path[-1].get("value", 0))
                        path.append({"op": "+", "a": last_val, "b": power, "result": last_val + power})
                        return path
            except (OverflowError, ValueError):
                break
    return None


def _solve_mul_exp(target, extractable):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    for base in sorted(extractable):
        if base <= 1:
            continue
        for exp in range(2, 20):
            try:
                power = base ** exp
                if power > target:
                    break
                if power == target:
                    path = [
                        {"op": "extract", "value": base},
                    ]
                    for _ in range(exp - 1):
                        last_val = path[-1].get("result", path[-1].get("value", 0))
                        path.append({"op": "*", "a": last_val, "b": base, "result": last_val * base})
                    return path
                if target % power == 0:
                    quotient = target // power
                    sub = _get_factorizations(quotient, extractable)
                    if sub:
                        path = list(sub)
                        last_val = path[-1].get("result", path[-1].get("value", 0))
                        path.append({"op": "*", "a": last_val, "b": power, "result": last_val * power})
                        return path
            except (OverflowError, ValueError):
                break
    return None


def _solve_exp_only(target, extractable):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    for base in sorted(extractable):
        if base <= 1:
            continue
        for exp in extractable:
            if exp <= 1:
                continue
            try:
                if base ** exp == target:
                    path = [{"op": "extract", "value": base}]
                    for _ in range(exp - 1):
                        last_val = path[-1].get("result", path[-1].get("value", 0))
                        path.append({"op": "*", "a": last_val, "b": base, "result": last_val * base})
                    return path
            except (OverflowError, ValueError):
                break
    return None


def _solve_bfs(target, extractable, ops, max_steps=200):
    if target in extractable:
        return [{"op": "extract", "value": target}]

    queue = deque()
    visited = set()

    for num in extractable:
        path = [{"op": "extract", "value": num}]
        queue.append((num, path))
        visited.add(num)

    while queue:
        current, path = queue.popleft()

        if len(path) > max_steps:
            continue

        for num in extractable:
            for op_name in ops:
                result = None
                new_path = None

                if op_name == '+':
                    result = current + num
                    if 0 < result <= 10**12 and result not in visited:
                        new_path = path + [{"op": "+", "a": current, "b": num, "result": result}]

                elif op_name == '-' and current > num:
                    result = current - num
                    if 0 < result <= 10**12 and result not in visited:
                        new_path = path + [{"op": "-", "a": current, "b": num, "result": result}]

                elif op_name == '*':
                    result = current * num
                    if 0 < result <= 10**12 and result not in visited:
                        new_path = path + [{"op": "*", "a": current, "b": num, "result": result}]

                elif op_name == '/' and num > 0 and current >= num and current % num == 0:
                    result = current // num
                    if 0 < result <= 10**12 and result not in visited:
                        new_path = path + [{"op": "/", "a": current, "b": num, "result": result}]

                elif op_name == '^' and num > 1 and current > 1:
                    try:
                        result = current ** num
                        if 0 < result <= 10**12 and result not in visited:
                            new_path = path + [{"op": "^", "a": current, "b": num, "result": result}]
                    except (OverflowError, ValueError):
                        pass

                if new_path and result:
                    visited.add(result)
                    if result == target:
                        return new_path
                    queue.append((result, new_path))

    return None


def _build_error_message(target, extractable, ops):
    hints = []

    if not ops:
        hints.append("Enable at least one operation.")
    elif '+' not in ops and '*' not in ops and '^' not in ops:
        hints.append("Enable at least Addition (+) or Multiplication (*) to reach most numbers.")
    elif '*' not in ops and '+' in ops:
        g = _gcd_of_list(extractable) if extractable else 1
        if g > 1 and target % g != 0:
            hints.append(f"With only addition, numbers {extractable} can only make multiples of {g}.")
            hints.append(f"Target {target} is not divisible by {g}. Add a number that breaks the pattern or enable Multiplication.")
    elif '+' not in ops and '*' in ops:
        g = _gcd_of_list(extractable) if extractable else 1
        if g > 1 and target % g != 0:
            hints.append(f"With only multiplication, you can only make multiples of {g}.")
            hints.append(f"Target {target} is not divisible by {g}. Enable Addition (+) to reach it.")

    if not hints:
        hints.append(f"Cannot reach {target} with extractable {extractable} and operations {sorted(ops)}.")
        hints.append("Try enabling more operations or adding more extractable numbers.")

    return " | ".join(hints)


def _gcd_of_list(nums):
    if not nums:
        return 1
    result = nums[0]
    for n in nums[1:]:
        result = math.gcd(result, n)
    return result


def format_solution(path):
    if not path:
        return "No solution found"

    lines = []
    for step in path:
        if step["op"] == "extract":
            lines.append(f"Extract {step['value']}")
        else:
            op_symbols = {"+": "+", "-": "-", "*": "x", "/": "/", "^": "^"}
            op_sym = op_symbols.get(step["op"], step["op"])
            lines.append(f"{step['a']} {op_sym} {step['b']} = {step['result']}")

    return lines


def get_needed_buildings(path):
    if not path:
        return {}

    buildings = {"extractors": set(), "adders": 0, "multipliers": 0,
                 "subtractors": 0, "dividers": 0, "exponentiators": 0}

    for step in path:
        if step["op"] == "extract":
            buildings["extractors"].add(step["value"])
        elif step["op"] == "+":
            buildings["adders"] += 1
        elif step["op"] == "*":
            buildings["multipliers"] += 1
        elif step["op"] == "-":
            buildings["subtractors"] += 1
        elif step["op"] == "/":
            buildings["dividers"] += 1
        elif step["op"] == "^":
            buildings["exponentiators"] += 1

    buildings["extractors"] = sorted(buildings["extractors"])
    return buildings
