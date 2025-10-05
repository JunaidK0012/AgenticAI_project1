from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query).get("v", [None])[0]



@tool
def youtube_transcript_tool(video_url: str) -> str:
    """
    Fetches the transcript of a YouTube video.

    Input:
    - video_url (str): The full YouTube video URL (e.g., "https://www.youtube.com/watch?v=abc123").

    Behavior:
    - Extracts the video ID from the URL.
    - Attempts to fetch the English transcript using the YouTube Transcript API.
    - Concatenates all transcript segments into a single text string.

    Output:
    - A plain text transcript of the video (without timestamps).
    - If no transcript is available or an error occurs, returns a descriptive error message.

    Notes for LLM:
    - Use this tool when the user asks for a video summary, transcript, or explanation of YouTube content.
    - Do not attempt to answer directly without calling this tool if transcript access is required.
    """

    try:
        video_id = extract_video_id(video_url)
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id,languages=['en']).to_raw_data()

        output = ""
        for t in transcript:
            output += t['text']
        
        return output

    except Exception as e:
        return f"Could not fetch transcript: {e}"

