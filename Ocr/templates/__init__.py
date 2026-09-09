"""
Answer sheet templates and specific OMR detectors.
"""
from templates.omr_20 import OMR20Detector, TemplateConfig20
from templates.omr_50 import OMR50Detector, TemplateConfig50

__all__ = [
    "OMR20Detector",
    "TemplateConfig20",
    "OMR50Detector",
    "TemplateConfig50",
]
