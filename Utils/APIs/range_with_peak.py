import numpy as np

def rangeWithPeak(start:int, end:int, peak:int, peak_width='normal'):
    # Standard deviation (spread) for each width type
    width_mapping = {
        'wide': (end - start) / 3,  # Wider spread
        'normal': (end - start) / 5,  # Moderate spread
        'narrow': (end - start) / 8  # Narrow spread
    }

    # Ensure peak_width is valid
    if peak_width not in width_mapping:
        raise ValueError(f"invalid peak_width value {peak_width}, peak_width must be 'wide', 'normal', or 'narrow'")

    if peak < start or peak > end:
        raise ValueError(f"invalid peak value {peak}, peak must be between {start} to {end}")

    std_dev = width_mapping[peak_width]

    while True:
        # Generate a candidate value from a normal distribution centered at the peak
        candidate = int(np.random.normal(peak, std_dev))
        #candidate = int(random.normalvariate(peak, std_dev))

        # Return only if the candidate is within the start and end range
        if start <= candidate <= end:
            return candidate
