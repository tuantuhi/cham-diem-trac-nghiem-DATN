"""
Core OMR processing engine.

Provides the base classes and utilities for OMR (Optical Mark Recognition)
detection across different answer sheet templates.

Quick start:
    from core import FiducialOMRDetector, TemplateConfig

    detector = FiducialOMRDetector()
    result = detector.process("path/to/image.jpg")
"""
from core.config import ANSWER_MAP, BubbleROI, TemplateConfig
from core.calibrator import GridAutoCalibrator
from core.detector import FiducialOMRDetector
from core.marker import FiducialMarkerDetector

__all__ = [
    "ANSWER_MAP",
    "BubbleROI",
    "TemplateConfig",
    "FiducialMarkerDetector",
    "GridAutoCalibrator",
    "FiducialOMRDetector",
]
