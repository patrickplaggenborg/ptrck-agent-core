---
name: youtube-transcript
description: Fetch transcripts from YouTube videos with timestamps. This skill should be used when the user pastes a YouTube URL, asks for a video transcript, or wants to know what's said at a specific point in a video. Handles youtube.com and youtu.be URLs, including timestamp parameters (t=).
---

# YouTube Transcript

Fetch and display transcripts from YouTube videos with timestamps using the `youtube-transcript-api` library.

## Usage

To fetch a transcript, run the script with a YouTube URL or video ID:

```bash
python scripts/youtube_transcript.py "<youtube_url>"
```

The script handles various URL formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&t=20s`
- `https://youtu.be/VIDEO_ID`
- `https://youtu.be/VIDEO_ID?t=120`
- Just the video ID: `VIDEO_ID`

## Video Position Feature

When a URL contains a timestamp parameter (`t=`), the script inserts a position indicator showing where that timestamp falls in the transcript:

```
[0:00] Hey everyone, welcome back to the channel
[0:05] Today we're going to talk about...
[0:18] So the first thing I want to mention is...
>>> [VIDEO POSITION: 0:20] <<<
[0:25] And that's really important because...
```

This helps identify what's being discussed at the specific point the user linked to.

## Requirements

Install the required library:

```bash
pip install youtube-transcript-api
```

## Limitations

- Only works for videos that have transcripts (auto-generated or manual captions)
- Some videos may have transcripts disabled by the uploader
- The library may be blocked by YouTube if used excessively from cloud IPs
