def truncate_float(num: float):
    return float('%.1f'%(num))

def normalize_range(old_value, old_min, old_max, new_min, new_max):
    old_range = old_max - old_min
    if old_range == 0:
        raise ValueError("old_range is 0")
    new_range = new_max - new_min
    new_value = (((old_value - old_min) * new_range) / old_range) + new_min
    return new_value

