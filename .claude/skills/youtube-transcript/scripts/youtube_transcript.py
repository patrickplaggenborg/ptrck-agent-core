#!/usr/bin/env python3
"""
Fetch YouTube video transcripts with timestamps.

Usage:
    python youtube_transcript.py <youtube_url_or_video_id>

Examples:
    python youtube_transcript.py "https://www.youtube.com/watch?v=O6JZU2LVAZk&t=20s"
    python youtube_transcript.py "https://youtu.be/O6JZU2LVAZk?t=120"
    python youtube_transcript.py O6JZU2LVAZk

Requires: pip install youtube-transcript-api
"""

import re
import sys
from urllib.parse import parse_qs, urlparse


def parse_youtube_url(url_or_id: str) -> tuple[str, int | None]:
    """
    Parse a YouTube URL or video ID and extract the video ID and optional timestamp.

    Returns:
        tuple: (video_id, timestamp_seconds or None)
    """
    url_or_id = url_or_id.strip()

    # If it's just a video ID (11 characters, alphanumeric with - and _)
    if re.match(r'^[\w-]{11}$', url_or_id):
        return url_or_id, None

    parsed = urlparse(url_or_id)
    query_params = parse_qs(parsed.query)

    # Extract video ID
    video_id = None

    # youtube.com/watch?v=VIDEO_ID
    if 'v' in query_params:
        video_id = query_params['v'][0]
    # youtu.be/VIDEO_ID
    elif parsed.netloc in ('youtu.be', 'www.youtu.be'):
        video_id = parsed.path.lstrip('/')
    # youtube.com/embed/VIDEO_ID
    elif '/embed/' in parsed.path:
        video_id = parsed.path.split('/embed/')[-1].split('/')[0]
    # youtube.com/v/VIDEO_ID
    elif '/v/' in parsed.path:
        video_id = parsed.path.split('/v/')[-1].split('/')[0]

    if not video_id:
        raise ValueError(f"Could not extract video ID from: {url_or_id}")

    # Clean video ID (remove any trailing parameters)
    video_id = video_id.split('?')[0].split('&')[0]

    # Extract timestamp (t parameter)
    timestamp = None
    if 't' in query_params:
        t_value = query_params['t'][0]
        timestamp = parse_timestamp(t_value)

    return video_id, timestamp


def parse_timestamp(t_value: str) -> int:
    """
    Parse timestamp parameter into seconds.

    Handles formats like:
    - "20" (seconds)
    - "20s" (seconds)
    - "1m30s" (minutes and seconds)
    - "1h2m30s" (hours, minutes, seconds)
    - "90" (just a number = seconds)
    """
    t_value = t_value.strip().lower()

    # Try simple integer (seconds)
    if t_value.isdigit():
        return int(t_value)

    # Remove trailing 's' if it's just "20s"
    if re.match(r'^\d+s$', t_value):
        return int(t_value[:-1])

    # Parse complex format like "1h2m30s" or "2m30s"
    total_seconds = 0

    hours_match = re.search(r'(\d+)h', t_value)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600

    minutes_match = re.search(r'(\d+)m', t_value)
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60

    seconds_match = re.search(r'(\d+)s', t_value)
    if seconds_match:
        total_seconds += int(seconds_match.group(1))

    return total_seconds if total_seconds > 0 else int(re.sub(r'[^\d]', '', t_value) or 0)


def format_time(seconds: float) -> str:
    """Format seconds into [H:MM:SS] or [M:SS] format."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def fetch_transcript(video_id: str, video_position: int | None = None) -> str:
    """
    Fetch transcript for a YouTube video and format it with timestamps.

    Args:
        video_id: YouTube video ID
        video_position: Optional position in seconds to mark in the transcript

    Returns:
        Formatted transcript string with timestamps
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return "Error: youtube-transcript-api is not installed. Run: pip install youtube-transcript-api"

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
    except Exception as e:
        return f"Error fetching transcript: {e}"

    lines = []
    position_inserted = False

    for snippet in transcript.snippets:
        start_time = snippet.start
        text = snippet.text.replace('\n', ' ').strip()

        # Insert video position indicator at the right place
        if video_position is not None and not position_inserted:
            if start_time >= video_position:
                lines.append(f">>> [VIDEO POSITION: {format_time(video_position)}] <<<")
                position_inserted = True

        lines.append(f"[{format_time(start_time)}] {text}")

    # If position wasn't inserted (timestamp is after all content), add at end
    if video_position is not None and not position_inserted:
        lines.append(f">>> [VIDEO POSITION: {format_time(video_position)}] <<<")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube_transcript.py <youtube_url_or_video_id>")
        print("\nExamples:")
        print('  python youtube_transcript.py "https://www.youtube.com/watch?v=O6JZU2LVAZk&t=20s"')
        print('  python youtube_transcript.py "https://youtu.be/O6JZU2LVAZk"')
        print("  python youtube_transcript.py O6JZU2LVAZk")
        sys.exit(1)

    url_or_id = sys.argv[1]

    try:
        video_id, video_position = parse_youtube_url(url_or_id)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Video ID: {video_id}")
    if video_position is not None:
        print(f"Video Position: {format_time(video_position)} ({video_position}s)")
    print("-" * 50)
    print()

    transcript = fetch_transcript(video_id, video_position)
    print(transcript)


if __name__ == "__main__":
    main()
