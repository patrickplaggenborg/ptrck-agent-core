#!/usr/bin/env python3
"""
Figma REST API client for design extraction and analysis.

Commands:
    export         - Export frames/nodes as images (PNG, JPG, SVG, PDF)
    structure      - Get file/node structure as AI-optimized JSON
    tokens         - Extract design tokens (colors, typography, effects, spacing)
    components     - List published components and styles
    analyze        - Full analysis (structure + tokens + thumbnails)
    comments       - Get comments from a file
    comment-add    - Add a comment to a file
    comment-delete - Delete a comment
    versions       - Get version history of a file
    projects       - List team projects
    project-files  - List files in a project
    dev-resources  - Get dev resources from a file

Usage:
    python figma_api.py export --url "https://figma.com/file/ABC/Design" --output design.png
    python figma_api.py structure --url "https://figma.com/file/ABC/Design" --output structure.json
    python figma_api.py tokens --url "https://figma.com/file/ABC/Design" --output tokens.json
    python figma_api.py analyze --url "https://figma.com/file/ABC/Design" --output-dir ./export/
    python figma_api.py comments --url "https://figma.com/file/ABC/Design" --output comments.json
    python figma_api.py versions --url "https://figma.com/file/ABC/Design" --output versions.json
    python figma_api.py projects --team-id 12345 --output projects.json
    python figma_api.py dev-resources --url "https://figma.com/file/ABC/Design" --output dev_resources.json
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

try:
    import requests
except ImportError:
    print("Error: requests package not installed")
    print("Install with: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


FIGMA_API_BASE = "https://api.figma.com/v1"
CACHE_DIR = Path.home() / ".cache" / "figma-skill"
CACHE_TTL_HOURS = 1


def find_access_token() -> Optional[str]:
    """Find Figma access token from environment or .env files.

    Priority order:
    1. FIGMA_ACCESS_TOKEN environment variable
    2. ~/.claude/skills/figma/.env
    3. ~/.claude/skills/.env
    4. ~/.claude/.env
    5. Current directory .env
    """
    token = os.getenv('FIGMA_ACCESS_TOKEN')
    if token:
        return token

    if load_dotenv:
        env_locations = [
            Path(__file__).parent.parent / '.env',  # skill directory
            Path(__file__).parent.parent.parent / '.env',  # skills directory
            Path.home() / '.claude' / '.env',  # claude directory
            Path.cwd() / '.env',  # current directory
        ]

        for env_file in env_locations:
            if env_file.exists():
                load_dotenv(env_file)
                token = os.getenv('FIGMA_ACCESS_TOKEN')
                if token:
                    return token

    return None


def parse_figma_url(url: str) -> Tuple[str, Optional[str]]:
    """Parse Figma URL to extract file key and optional node ID.

    Supports:
        https://www.figma.com/file/{key}/{name}
        https://www.figma.com/file/{key}/{name}?node-id={id}
        https://www.figma.com/design/{key}/{name}
        https://www.figma.com/design/{key}/{name}?node-id={id}

    Returns:
        Tuple of (file_key, node_id or None)
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) >= 2 and path_parts[0] in ('file', 'design'):
        file_key = path_parts[1]
    else:
        raise ValueError(f"Invalid Figma URL: {url}")

    query_params = parse_qs(parsed.query)
    node_id = None
    if 'node-id' in query_params:
        # URL uses '-' but API uses ':'
        node_id = query_params['node-id'][0].replace('-', ':')

    return file_key, node_id


def get_cache_path(file_key: str, cache_type: str) -> Path:
    """Get cache file path for a given file key and type."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{file_key}_{cache_type}.json"


def load_cache(file_key: str, cache_type: str) -> Optional[Dict]:
    """Load cached data if valid (within TTL)."""
    cache_path = get_cache_path(file_key, cache_type)
    if not cache_path.exists():
        return None

    try:
        with open(cache_path) as f:
            cached = json.load(f)

        cached_time = datetime.fromisoformat(cached.get('_cached_at', '2000-01-01'))
        if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
            return cached
    except (json.JSONDecodeError, KeyError):
        pass

    return None


def save_cache(file_key: str, cache_type: str, data: Dict) -> None:
    """Save data to cache with timestamp."""
    cache_path = get_cache_path(file_key, cache_type)
    data['_cached_at'] = datetime.now().isoformat()
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)


def make_request(
    endpoint: str,
    token: str,
    params: Optional[Dict] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Make authenticated request to Figma API with retry logic."""
    headers = {
        'X-Figma-Token': token,
        'Content-Type': 'application/json'
    }
    url = f"{FIGMA_API_BASE}{endpoint}"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 429:
                wait_time = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue

            if response.status_code == 403:
                print("Error: Access forbidden. Check your FIGMA_ACCESS_TOKEN.", file=sys.stderr)
                sys.exit(1)

            if response.status_code == 404:
                print(f"Error: File not found or no access.", file=sys.stderr)
                sys.exit(1)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Timeout. Retry {attempt + 1} after {wait_time}s...", file=sys.stderr)
            time.sleep(wait_time)

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Error: {e}. Retry {attempt + 1} after {wait_time}s...", file=sys.stderr)
            time.sleep(wait_time)

    return {}


def get_file(file_key: str, token: str, use_cache: bool = True) -> Dict[str, Any]:
    """Get file metadata and document tree."""
    if use_cache:
        cached = load_cache(file_key, 'file')
        if cached:
            return cached

    data = make_request(f"/files/{file_key}", token)
    if use_cache and data:
        save_cache(file_key, 'file', data)
    return data


def get_file_nodes(
    file_key: str,
    node_ids: List[str],
    token: str
) -> Dict[str, Any]:
    """Get specific nodes from file."""
    params = {'ids': ','.join(node_ids)}
    return make_request(f"/files/{file_key}/nodes", token, params)


def get_image_urls(
    file_key: str,
    node_ids: List[str],
    token: str,
    scale: int = 2,
    format: str = 'png'
) -> Dict[str, str]:
    """Get image export URLs for nodes."""
    params = {
        'ids': ','.join(node_ids),
        'scale': scale,
        'format': format
    }
    response = make_request(f"/images/{file_key}", token, params)
    return response.get('images', {})


def get_file_styles(file_key: str, token: str) -> Dict[str, Any]:
    """Get published styles from file."""
    return make_request(f"/files/{file_key}/styles", token)


def get_file_components(file_key: str, token: str) -> Dict[str, Any]:
    """Get published components from file."""
    return make_request(f"/files/{file_key}/components", token)


def get_file_comments(file_key: str, token: str) -> Dict[str, Any]:
    """Get comments from file."""
    return make_request(f"/files/{file_key}/comments", token)


def post_comment(
    file_key: str,
    token: str,
    message: str,
    node_id: Optional[str] = None,
    client_meta: Optional[Dict] = None
) -> Dict[str, Any]:
    """Post a comment to a file."""
    headers = {
        'X-Figma-Token': token,
        'Content-Type': 'application/json'
    }
    url = f"{FIGMA_API_BASE}/files/{file_key}/comments"

    data: Dict[str, Any] = {'message': message}
    if client_meta:
        data['client_meta'] = client_meta
    elif node_id:
        # If node_id provided without client_meta, create a node-anchored comment
        data['client_meta'] = {'node_id': node_id}

    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    return response.json()


def delete_comment(file_key: str, comment_id: str, token: str) -> bool:
    """Delete a comment from file."""
    headers = {
        'X-Figma-Token': token,
        'Content-Type': 'application/json'
    }
    url = f"{FIGMA_API_BASE}/files/{file_key}/comments/{comment_id}"

    response = requests.delete(url, headers=headers, timeout=30)
    return response.status_code == 200


def get_file_versions(file_key: str, token: str) -> Dict[str, Any]:
    """Get version history of a file."""
    return make_request(f"/files/{file_key}/versions", token)


def get_team_projects(team_id: str, token: str) -> Dict[str, Any]:
    """Get projects for a team."""
    return make_request(f"/teams/{team_id}/projects", token)


def get_project_files(project_id: str, token: str) -> Dict[str, Any]:
    """Get files in a project."""
    return make_request(f"/projects/{project_id}/files", token)


def get_dev_resources(file_key: str, token: str, node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get dev resources from a file."""
    params = {}
    if node_ids:
        params['node_ids'] = ','.join(node_ids)
    return make_request(f"/files/{file_key}/dev_resources", token, params)


def download_image(url: str, output_path: Path, verbose: bool = False) -> bool:
    """Download image from URL to local path."""
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        if verbose:
            print(f"Downloaded: {output_path}")
        return True

    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False


def rgba_to_hex(color: Dict) -> str:
    """Convert Figma RGBA color to hex string."""
    r = int(color.get('r', 0) * 255)
    g = int(color.get('g', 0) * 255)
    b = int(color.get('b', 0) * 255)
    return f"#{r:02x}{g:02x}{b:02x}"


def rgba_to_css(color: Dict) -> str:
    """Convert Figma RGBA color to CSS rgba string."""
    r = int(color.get('r', 0) * 255)
    g = int(color.get('g', 0) * 255)
    b = int(color.get('b', 0) * 255)
    a = color.get('a', 1)
    if a < 1:
        return f"rgba({r}, {g}, {b}, {a:.2f})"
    return f"rgb({r}, {g}, {b})"


def extract_colors_from_node(node: Dict, colors: Dict) -> None:
    """Recursively extract colors from node fills and strokes."""
    # Extract from fills
    for fill in node.get('fills', []):
        if fill.get('type') == 'SOLID' and fill.get('visible', True):
            color = fill.get('color', {})
            hex_color = rgba_to_hex(color)
            if hex_color not in colors:
                colors[hex_color] = {
                    'hex': hex_color,
                    'rgb': [int(color.get('r', 0) * 255),
                            int(color.get('g', 0) * 255),
                            int(color.get('b', 0) * 255)],
                    'opacity': fill.get('opacity', 1),
                    'usedIn': []
                }
            colors[hex_color]['usedIn'].append(node.get('name', 'unknown'))

    # Recurse into children
    for child in node.get('children', []):
        extract_colors_from_node(child, colors)


def extract_typography_from_node(node: Dict, typography: Dict) -> None:
    """Recursively extract typography styles from text nodes."""
    if node.get('type') == 'TEXT':
        style = node.get('style', {})
        if style:
            font_key = f"{style.get('fontFamily', 'Unknown')}/{style.get('fontWeight', 400)}/{style.get('fontSize', 16)}"
            if font_key not in typography:
                typography[font_key] = {
                    'fontFamily': style.get('fontFamily', 'Unknown'),
                    'fontSize': style.get('fontSize', 16),
                    'fontWeight': style.get('fontWeight', 400),
                    'lineHeight': style.get('lineHeightPx', style.get('fontSize', 16) * 1.5),
                    'letterSpacing': style.get('letterSpacing', 0),
                    'textCase': style.get('textCase', 'ORIGINAL'),
                    'usedIn': []
                }
            typography[font_key]['usedIn'].append(node.get('name', 'unknown'))

    # Recurse into children
    for child in node.get('children', []):
        extract_typography_from_node(child, typography)


def extract_effects_from_node(node: Dict, effects_dict: Dict) -> None:
    """Recursively extract effects (shadows, blurs) from nodes."""
    for effect in node.get('effects', []):
        if effect.get('visible', True):
            effect_type = effect.get('type', 'UNKNOWN')
            color = effect.get('color', {})
            offset = effect.get('offset', {'x': 0, 'y': 0})

            effect_key = f"{effect_type}/{effect.get('radius', 0)}"
            if effect_key not in effects_dict:
                effects_dict[effect_key] = {
                    'type': effect_type,
                    'color': rgba_to_css(color),
                    'offset': {'x': offset.get('x', 0), 'y': offset.get('y', 0)},
                    'radius': effect.get('radius', 0),
                    'spread': effect.get('spread', 0),
                    'usedIn': []
                }
            effects_dict[effect_key]['usedIn'].append(node.get('name', 'unknown'))

    # Recurse into children
    for child in node.get('children', []):
        extract_effects_from_node(child, effects_dict)


def extract_spacing_from_node(node: Dict, spacing_values: set) -> None:
    """Recursively extract spacing values from node padding and gaps."""
    # Auto-layout spacing
    if node.get('layoutMode'):
        spacing_values.add(node.get('itemSpacing', 0))
        spacing_values.add(node.get('paddingTop', 0))
        spacing_values.add(node.get('paddingRight', 0))
        spacing_values.add(node.get('paddingBottom', 0))
        spacing_values.add(node.get('paddingLeft', 0))

    # Recurse into children
    for child in node.get('children', []):
        extract_spacing_from_node(child, spacing_values)


def simplify_node(node: Dict, depth: int = 0, max_depth: int = 10) -> Dict:
    """Simplify node structure for AI-optimized output."""
    simplified = {
        'id': node.get('id'),
        'name': node.get('name'),
        'type': node.get('type'),
    }

    # Add dimensions if available
    bbox = node.get('absoluteBoundingBox', {})
    if bbox:
        simplified['width'] = bbox.get('width')
        simplified['height'] = bbox.get('height')

    # Add layout info
    if node.get('layoutMode'):
        simplified['layout'] = {
            'mode': node.get('layoutMode'),
            'direction': 'horizontal' if node.get('layoutMode') == 'HORIZONTAL' else 'vertical',
            'gap': node.get('itemSpacing', 0),
            'padding': {
                'top': node.get('paddingTop', 0),
                'right': node.get('paddingRight', 0),
                'bottom': node.get('paddingBottom', 0),
                'left': node.get('paddingLeft', 0),
            }
        }

    # Add text content for text nodes
    if node.get('type') == 'TEXT':
        simplified['text'] = node.get('characters', '')
        style = node.get('style', {})
        if style:
            simplified['textStyle'] = {
                'font': style.get('fontFamily'),
                'size': style.get('fontSize'),
                'weight': style.get('fontWeight'),
            }

    # Recurse into children (with depth limit)
    if depth < max_depth and node.get('children'):
        simplified['children'] = [
            simplify_node(child, depth + 1, max_depth)
            for child in node.get('children', [])
        ]

    return simplified


def find_frames(node: Dict, frames: List[Dict]) -> None:
    """Find all FRAME nodes in the tree."""
    if node.get('type') == 'FRAME':
        frames.append(node)
    for child in node.get('children', []):
        find_frames(child, frames)


# ============================================================================
# Command: export
# ============================================================================

def cmd_export(args, token: str) -> None:
    """Export frames/nodes as images."""
    file_key, url_node_id = parse_figma_url(args.url)

    # Determine node IDs to export
    node_ids = []
    if args.node_ids:
        node_ids = [nid.replace('-', ':') for nid in args.node_ids.split(',')]
    elif url_node_id:
        node_ids = [url_node_id]
    else:
        # Get top-level frames from first page
        file_data = get_file(file_key, token, use_cache=not args.no_cache)
        document = file_data.get('document', {})
        pages = document.get('children', [])
        if pages:
            frames = []
            find_frames(pages[0], frames)
            # Get top-level frames only (limit to 10)
            node_ids = [f['id'] for f in frames[:10]]

    if not node_ids:
        print("No frames found to export", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Exporting {len(node_ids)} node(s)...")

    # Get image URLs
    image_urls = get_image_urls(file_key, node_ids, token, args.scale, args.format)

    # Determine output handling
    output_path = Path(args.output)
    is_single_file = output_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']

    if is_single_file and len(node_ids) == 1:
        # Single file output
        url = image_urls.get(node_ids[0])
        if url:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            download_image(url, output_path, args.verbose)
            print(f"Exported: {output_path}")
        else:
            print("Failed to get image URL", file=sys.stderr)
            sys.exit(1)
    else:
        # Directory output
        output_dir = output_path if not is_single_file else output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        exported = 0
        for node_id, url in image_urls.items():
            if url:
                safe_id = node_id.replace(':', '-')
                file_path = output_dir / f"frame_{safe_id}.{args.format}"
                if download_image(url, file_path, args.verbose):
                    exported += 1

        print(f"Exported {exported} file(s) to: {output_dir}")


# ============================================================================
# Command: structure
# ============================================================================

def cmd_structure(args, token: str) -> None:
    """Get file/node structure as AI-optimized JSON."""
    file_key, url_node_id = parse_figma_url(args.url)

    file_data = get_file(file_key, token, use_cache=not args.no_cache)

    # Build AI-optimized structure
    output = {
        'file': {
            'key': file_key,
            'name': file_data.get('name', 'Unknown'),
            'lastModified': file_data.get('lastModified'),
            'version': file_data.get('version'),
        },
        'pages': []
    }

    document = file_data.get('document', {})
    for page in document.get('children', []):
        page_data = {
            'id': page.get('id'),
            'name': page.get('name'),
            'frames': []
        }

        for child in page.get('children', []):
            if child.get('type') in ['FRAME', 'COMPONENT', 'COMPONENT_SET']:
                page_data['frames'].append(simplify_node(child, max_depth=args.depth))

        output['pages'].append(page_data)

    # Add styles summary
    if 'styles' in file_data:
        output['styles'] = {}
        for style_id, style in file_data.get('styles', {}).items():
            style_type = style.get('styleType', 'UNKNOWN')
            if style_type not in output['styles']:
                output['styles'][style_type] = []
            output['styles'][style_type].append({
                'id': style_id,
                'name': style.get('name'),
                'description': style.get('description', '')
            })

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Structure saved to: {output_path}")

    # Print summary
    total_frames = sum(len(p['frames']) for p in output['pages'])
    print(f"  Pages: {len(output['pages'])}")
    print(f"  Frames: {total_frames}")


# ============================================================================
# Command: tokens
# ============================================================================

def cmd_tokens(args, token: str) -> None:
    """Extract design tokens (colors, typography, effects, spacing)."""
    file_key, _ = parse_figma_url(args.url)

    file_data = get_file(file_key, token, use_cache=not args.no_cache)

    colors = {}
    typography = {}
    effects = {}
    spacing_values = set()

    # Extract from document tree
    document = file_data.get('document', {})
    for page in document.get('children', []):
        extract_colors_from_node(page, colors)
        extract_typography_from_node(page, typography)
        extract_effects_from_node(page, effects)
        extract_spacing_from_node(page, spacing_values)

    # Also extract from published styles
    for style_id, style in file_data.get('styles', {}).items():
        style_type = style.get('styleType')
        style_name = style.get('name', style_id)

        if style_type == 'FILL':
            # Mark as a defined style
            for hex_color in colors:
                if style_name in str(colors[hex_color].get('usedIn', [])):
                    colors[hex_color]['styleName'] = style_name

    # Build output
    output = {
        'colors': colors,
        'typography': typography,
        'effects': effects,
        'spacing': sorted([s for s in spacing_values if s > 0])
    }

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Tokens saved to: {output_path}")
    print(f"  Colors: {len(colors)}")
    print(f"  Typography: {len(typography)}")
    print(f"  Effects: {len(effects)}")
    print(f"  Spacing values: {len(output['spacing'])}")


# ============================================================================
# Command: components
# ============================================================================

def cmd_components(args, token: str) -> None:
    """List published components and styles."""
    file_key, _ = parse_figma_url(args.url)

    if args.verbose:
        print("Fetching components and styles...")

    # Get components
    components_data = get_file_components(file_key, token)

    # Get styles
    styles_data = get_file_styles(file_key, token)

    output = {
        'components': [],
        'styles': {
            'colors': [],
            'typography': [],
            'effects': [],
            'grids': []
        }
    }

    # Process components
    for comp in components_data.get('meta', {}).get('components', []):
        output['components'].append({
            'key': comp.get('key'),
            'name': comp.get('name'),
            'description': comp.get('description', ''),
            'containingFrame': comp.get('containing_frame', {}).get('name'),
        })

    # Process styles
    for style in styles_data.get('meta', {}).get('styles', []):
        style_info = {
            'key': style.get('key'),
            'name': style.get('name'),
            'description': style.get('description', ''),
        }
        style_type = style.get('style_type', '').upper()

        if style_type == 'FILL':
            output['styles']['colors'].append(style_info)
        elif style_type == 'TEXT':
            output['styles']['typography'].append(style_info)
        elif style_type == 'EFFECT':
            output['styles']['effects'].append(style_info)
        elif style_type == 'GRID':
            output['styles']['grids'].append(style_info)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Components saved to: {output_path}")
    print(f"  Components: {len(output['components'])}")
    print(f"  Color styles: {len(output['styles']['colors'])}")
    print(f"  Text styles: {len(output['styles']['typography'])}")
    print(f"  Effect styles: {len(output['styles']['effects'])}")


# ============================================================================
# Command: analyze
# ============================================================================

def cmd_analyze(args, token: str) -> None:
    """Full analysis: structure + tokens + thumbnails."""
    file_key, url_node_id = parse_figma_url(args.url)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing Figma file: {file_key}")
    print(f"Output directory: {output_dir}")
    print()

    # 1. Get file structure
    print("1. Fetching file structure...")
    file_data = get_file(file_key, token, use_cache=not args.no_cache)

    structure_output = {
        'file': {
            'key': file_key,
            'name': file_data.get('name', 'Unknown'),
            'lastModified': file_data.get('lastModified'),
        },
        'pages': []
    }

    all_frame_ids = []
    document = file_data.get('document', {})
    for page in document.get('children', []):
        page_data = {
            'id': page.get('id'),
            'name': page.get('name'),
            'frames': []
        }

        for child in page.get('children', []):
            if child.get('type') in ['FRAME', 'COMPONENT', 'COMPONENT_SET']:
                page_data['frames'].append(simplify_node(child, max_depth=5))
                all_frame_ids.append(child.get('id'))

        structure_output['pages'].append(page_data)

    with open(output_dir / 'structure.json', 'w') as f:
        json.dump(structure_output, f, indent=2)

    total_frames = sum(len(p['frames']) for p in structure_output['pages'])
    print(f"   Pages: {len(structure_output['pages'])}, Frames: {total_frames}")

    # 2. Extract design tokens
    print("2. Extracting design tokens...")
    colors = {}
    typography = {}
    effects = {}
    spacing_values = set()

    for page in document.get('children', []):
        extract_colors_from_node(page, colors)
        extract_typography_from_node(page, typography)
        extract_effects_from_node(page, effects)
        extract_spacing_from_node(page, spacing_values)

    tokens_output = {
        'colors': colors,
        'typography': typography,
        'effects': effects,
        'spacing': sorted([s for s in spacing_values if s > 0])
    }

    with open(output_dir / 'tokens.json', 'w') as f:
        json.dump(tokens_output, f, indent=2)

    print(f"   Colors: {len(colors)}, Typography: {len(typography)}, Effects: {len(effects)}")

    # 3. Export frame thumbnails
    if all_frame_ids and not args.no_images:
        print("3. Exporting frame thumbnails...")
        thumbnails_dir = output_dir / 'thumbnails'
        thumbnails_dir.mkdir(exist_ok=True)

        # Limit to first 20 frames to avoid rate limits
        export_ids = all_frame_ids[:20]
        image_urls = get_image_urls(file_key, export_ids, token, scale=1, format='png')

        exported = 0
        for node_id, url in image_urls.items():
            if url:
                safe_id = node_id.replace(':', '-')
                if download_image(url, thumbnails_dir / f"{safe_id}.png", verbose=False):
                    exported += 1

        print(f"   Exported {exported} thumbnail(s)")
    else:
        print("3. Skipping thumbnails (--no-images or no frames found)")

    # 4. Create summary
    print("4. Creating analysis summary...")
    summary = {
        'file': structure_output['file'],
        'summary': {
            'pages': len(structure_output['pages']),
            'frames': total_frames,
            'colors': len(colors),
            'typography': len(typography),
            'effects': len(effects),
            'spacingValues': len(tokens_output['spacing']),
        },
        'colorPalette': list(colors.keys())[:20],  # Top 20 colors
        'fontFamilies': list(set(t['fontFamily'] for t in typography.values())),
        'spacingScale': tokens_output['spacing'][:10],  # First 10 spacing values
    }

    with open(output_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print()
    print("Analysis complete!")
    print(f"  - structure.json: File and frame hierarchy")
    print(f"  - tokens.json: Design tokens (colors, typography, effects)")
    print(f"  - summary.json: Quick overview for AI consumption")
    if not args.no_images:
        print(f"  - thumbnails/: Frame preview images")


# ============================================================================
# Command: comments
# ============================================================================

def cmd_comments(args, token: str) -> None:
    """Get comments from a file."""
    file_key, _ = parse_figma_url(args.url)

    if args.verbose:
        print("Fetching comments...")

    comments_data = get_file_comments(file_key, token)

    output = {
        'comments': []
    }

    for comment in comments_data.get('comments', []):
        comment_info = {
            'id': comment.get('id'),
            'message': comment.get('message'),
            'user': {
                'handle': comment.get('user', {}).get('handle'),
                'name': comment.get('user', {}).get('handle'),
                'img_url': comment.get('user', {}).get('img_url'),
            },
            'created_at': comment.get('created_at'),
            'resolved_at': comment.get('resolved_at'),
            'order_id': comment.get('order_id'),
        }

        # Include node reference if available
        client_meta = comment.get('client_meta', {})
        if client_meta:
            comment_info['node_id'] = client_meta.get('node_id')
            comment_info['node_offset'] = client_meta.get('node_offset')

        output['comments'].append(comment_info)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Comments saved to: {output_path}")
    print(f"  Total comments: {len(output['comments'])}")
    resolved = sum(1 for c in output['comments'] if c.get('resolved_at'))
    print(f"  Resolved: {resolved}")
    print(f"  Open: {len(output['comments']) - resolved}")


def cmd_comment_add(args, token: str) -> None:
    """Add a comment to a file."""
    file_key, url_node_id = parse_figma_url(args.url)

    # Use node_id from args or from URL
    node_id = args.node_id or url_node_id

    if args.verbose:
        print(f"Posting comment to file {file_key}...")
        if node_id:
            print(f"  Attached to node: {node_id}")

    result = post_comment(file_key, token, args.message, node_id)

    print(f"Comment posted successfully!")
    print(f"  Comment ID: {result.get('id')}")
    print(f"  Message: {args.message[:50]}{'...' if len(args.message) > 50 else ''}")


def cmd_comment_delete(args, token: str) -> None:
    """Delete a comment from a file."""
    file_key, _ = parse_figma_url(args.url)

    if args.verbose:
        print(f"Deleting comment {args.comment_id}...")

    success = delete_comment(file_key, args.comment_id, token)

    if success:
        print(f"Comment {args.comment_id} deleted successfully!")
    else:
        print(f"Failed to delete comment {args.comment_id}", file=sys.stderr)
        sys.exit(1)


# ============================================================================
# Command: versions
# ============================================================================

def cmd_versions(args, token: str) -> None:
    """Get version history of a file."""
    file_key, _ = parse_figma_url(args.url)

    if args.verbose:
        print("Fetching version history...")

    versions_data = get_file_versions(file_key, token)

    output = {
        'versions': []
    }

    for version in versions_data.get('versions', []):
        version_info = {
            'id': version.get('id'),
            'created_at': version.get('created_at'),
            'label': version.get('label'),
            'description': version.get('description'),
            'user': {
                'handle': version.get('user', {}).get('handle'),
                'name': version.get('user', {}).get('handle'),
                'img_url': version.get('user', {}).get('img_url'),
            },
        }
        output['versions'].append(version_info)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Versions saved to: {output_path}")
    print(f"  Total versions: {len(output['versions'])}")

    # Show recent versions
    if output['versions']:
        print(f"  Latest: {output['versions'][0].get('created_at', 'Unknown')}")
        if output['versions'][0].get('label'):
            print(f"    Label: {output['versions'][0].get('label')}")


# ============================================================================
# Command: projects
# ============================================================================

def cmd_projects(args, token: str) -> None:
    """List team projects."""
    if args.verbose:
        print(f"Fetching projects for team {args.team_id}...")

    projects_data = get_team_projects(args.team_id, token)

    output = {
        'team_id': args.team_id,
        'projects': []
    }

    for project in projects_data.get('projects', []):
        output['projects'].append({
            'id': project.get('id'),
            'name': project.get('name'),
        })

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Projects saved to: {output_path}")
    print(f"  Total projects: {len(output['projects'])}")


def cmd_project_files(args, token: str) -> None:
    """List files in a project."""
    if args.verbose:
        print(f"Fetching files for project {args.project_id}...")

    files_data = get_project_files(args.project_id, token)

    output = {
        'project_id': args.project_id,
        'files': []
    }

    for file in files_data.get('files', []):
        output['files'].append({
            'key': file.get('key'),
            'name': file.get('name'),
            'thumbnail_url': file.get('thumbnail_url'),
            'last_modified': file.get('last_modified'),
        })

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Files saved to: {output_path}")
    print(f"  Total files: {len(output['files'])}")


# ============================================================================
# Command: dev-resources
# ============================================================================

def cmd_dev_resources(args, token: str) -> None:
    """Get dev resources from a file."""
    file_key, url_node_id = parse_figma_url(args.url)

    node_ids = None
    if args.node_ids:
        node_ids = [nid.replace('-', ':') for nid in args.node_ids.split(',')]
    elif url_node_id:
        node_ids = [url_node_id]

    if args.verbose:
        print("Fetching dev resources...")

    resources_data = get_dev_resources(file_key, token, node_ids)

    output = {
        'dev_resources': []
    }

    for resource in resources_data.get('dev_resources', []):
        resource_info = {
            'id': resource.get('id'),
            'name': resource.get('name'),
            'url': resource.get('url'),
            'file_key': resource.get('file_key'),
            'node_id': resource.get('node_id'),
        }
        output['dev_resources'].append(resource_info)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Dev resources saved to: {output_path}")
    print(f"  Total resources: {len(output['dev_resources'])}")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Figma REST API client for design extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # export command
    export_parser = subparsers.add_parser('export', help='Export frames as images')
    export_parser.add_argument('--url', required=True, help='Figma file or frame URL')
    export_parser.add_argument('--output', '-o', default='output', help='Output path (file or directory)')
    export_parser.add_argument('--scale', type=int, default=2, choices=[1, 2, 3, 4], help='Export scale')
    export_parser.add_argument('--format', '-f', default='png', choices=['png', 'jpg', 'svg', 'pdf'], help='Export format')
    export_parser.add_argument('--node-ids', help='Comma-separated node IDs to export')
    export_parser.add_argument('--no-cache', action='store_true', help='Bypass cache')
    export_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # structure command
    structure_parser = subparsers.add_parser('structure', help='Get file structure as JSON')
    structure_parser.add_argument('--url', required=True, help='Figma file URL')
    structure_parser.add_argument('--output', '-o', default='structure.json', help='Output JSON file')
    structure_parser.add_argument('--depth', type=int, default=5, help='Max depth for node tree')
    structure_parser.add_argument('--no-cache', action='store_true', help='Bypass cache')
    structure_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # tokens command
    tokens_parser = subparsers.add_parser('tokens', help='Extract design tokens')
    tokens_parser.add_argument('--url', required=True, help='Figma file URL')
    tokens_parser.add_argument('--output', '-o', default='tokens.json', help='Output JSON file')
    tokens_parser.add_argument('--no-cache', action='store_true', help='Bypass cache')
    tokens_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # components command
    components_parser = subparsers.add_parser('components', help='List published components and styles')
    components_parser.add_argument('--url', required=True, help='Figma file URL')
    components_parser.add_argument('--output', '-o', default='components.json', help='Output JSON file')
    components_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Full analysis (structure + tokens + thumbnails)')
    analyze_parser.add_argument('--url', required=True, help='Figma file URL')
    analyze_parser.add_argument('--output-dir', '-o', default='figma-export', help='Output directory')
    analyze_parser.add_argument('--no-cache', action='store_true', help='Bypass cache')
    analyze_parser.add_argument('--no-images', action='store_true', help='Skip thumbnail export')
    analyze_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # comments command
    comments_parser = subparsers.add_parser('comments', help='Get comments from a file')
    comments_parser.add_argument('--url', required=True, help='Figma file URL')
    comments_parser.add_argument('--output', '-o', default='comments.json', help='Output JSON file')
    comments_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # comment-add command
    comment_add_parser = subparsers.add_parser('comment-add', help='Add a comment to a file')
    comment_add_parser.add_argument('--url', required=True, help='Figma file URL')
    comment_add_parser.add_argument('--message', '-m', required=True, help='Comment message')
    comment_add_parser.add_argument('--node-id', help='Node ID to attach comment to')
    comment_add_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # comment-delete command
    comment_delete_parser = subparsers.add_parser('comment-delete', help='Delete a comment')
    comment_delete_parser.add_argument('--url', required=True, help='Figma file URL')
    comment_delete_parser.add_argument('--comment-id', required=True, help='Comment ID to delete')
    comment_delete_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # versions command
    versions_parser = subparsers.add_parser('versions', help='Get version history of a file')
    versions_parser.add_argument('--url', required=True, help='Figma file URL')
    versions_parser.add_argument('--output', '-o', default='versions.json', help='Output JSON file')
    versions_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # projects command
    projects_parser = subparsers.add_parser('projects', help='List team projects')
    projects_parser.add_argument('--team-id', required=True, help='Team ID')
    projects_parser.add_argument('--output', '-o', default='projects.json', help='Output JSON file')
    projects_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # project-files command
    project_files_parser = subparsers.add_parser('project-files', help='List files in a project')
    project_files_parser.add_argument('--project-id', required=True, help='Project ID')
    project_files_parser.add_argument('--output', '-o', default='project_files.json', help='Output JSON file')
    project_files_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    # dev-resources command
    dev_resources_parser = subparsers.add_parser('dev-resources', help='Get dev resources from a file')
    dev_resources_parser.add_argument('--url', required=True, help='Figma file URL')
    dev_resources_parser.add_argument('--node-ids', help='Comma-separated node IDs to filter')
    dev_resources_parser.add_argument('--output', '-o', default='dev_resources.json', help='Output JSON file')
    dev_resources_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get token
    token = find_access_token()
    if not token:
        print("Error: FIGMA_ACCESS_TOKEN not found", file=sys.stderr)
        print()
        print("Set via environment variable:")
        print("  export FIGMA_ACCESS_TOKEN='your-token'")
        print()
        print("Or create .env file with:")
        print("  FIGMA_ACCESS_TOKEN=your-token")
        print()
        print("Get your token at: https://www.figma.com/developers/api#access-tokens")
        sys.exit(1)

    # Run command
    if args.command == 'export':
        cmd_export(args, token)
    elif args.command == 'structure':
        cmd_structure(args, token)
    elif args.command == 'tokens':
        cmd_tokens(args, token)
    elif args.command == 'components':
        cmd_components(args, token)
    elif args.command == 'analyze':
        cmd_analyze(args, token)
    elif args.command == 'comments':
        cmd_comments(args, token)
    elif args.command == 'comment-add':
        cmd_comment_add(args, token)
    elif args.command == 'comment-delete':
        cmd_comment_delete(args, token)
    elif args.command == 'versions':
        cmd_versions(args, token)
    elif args.command == 'projects':
        cmd_projects(args, token)
    elif args.command == 'project-files':
        cmd_project_files(args, token)
    elif args.command == 'dev-resources':
        cmd_dev_resources(args, token)


if __name__ == '__main__':
    main()
