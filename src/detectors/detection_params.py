from typing import List

class DetectionParameters:
    def __init__(self, 
                 sampling_rate: int = 2000,
                 m_start: float = 0.045, 
                 m_end: float = 0.058,
                 h_start: float = 0.065, 
                 h_end: float = 0.085,
                 baseline_index: List[float] = [0.0001, 0.03],
                 std_cutoff: float = 9,
                 hard_cutoff: float = 50,
                 peak_width: float = 0.001):
        self.sampling_rate = sampling_rate
        self.m_start = m_start
        self.m_end = m_end
        self.h_start = h_start
        self.h_end = h_end
        self.baseline_index = baseline_index
        self.std_cutoff = std_cutoff
        self.hard_cutoff = hard_cutoff
        self.peak_width = peak_width
        self.roi_length = int(0.24 * sampling_rate)