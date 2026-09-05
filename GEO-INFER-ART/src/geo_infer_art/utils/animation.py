"""Shared animation-export helper for GEO-INFER-ART."""

import logging
import os

from matplotlib.animation import FuncAnimation

logger = logging.getLogger(__name__)


def save_animation_with_fallback(
    anim: FuncAnimation, output_path: str, fps: int
) -> str:
    """Save a matplotlib animation, falling back to GIF when ffmpeg is unavailable.

    Args:
        anim: The matplotlib animation to save.
        output_path: Desired output path. ``.gif`` targets are saved directly
            with the Pillow writer; any other extension is first attempted with
            ffmpeg and, on failure, re-saved as a ``.gif`` next to it.
        fps: Frames per second for the saved animation.

    Returns:
        The path the animation was actually saved to (differs from
        ``output_path`` only when the GIF fallback triggered).
    """
    directory = os.path.dirname(output_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    if output_path.lower().endswith(".gif"):
        anim.save(output_path, writer="pillow", fps=fps)
        return output_path

    try:
        anim.save(output_path, writer="ffmpeg", fps=fps)
    except Exception:
        # ffmpeg (or its matplotlib writer) is unavailable; fall back to GIF.
        gif_path = output_path.rsplit(".", 1)[0] + ".gif"
        logger.warning(
            "ffmpeg export failed for %s; falling back to GIF at %s",
            output_path,
            gif_path,
        )
        anim.save(gif_path, writer="pillow", fps=fps)
        return gif_path

    return output_path