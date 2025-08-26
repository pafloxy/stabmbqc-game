#!/usr/bin/env python3
"""Command-line tool to validate and generate campaign assets.

Usage:
    # Validate a campaign JSON file
    python -m backend.cli_generate --validate --in-json docs/levels/level-1.json

    # Validate with asset checking
    python -m backend.cli_generate --validate --in-json docs/levels/level-1.json --assets-dir docs/assets

    # Validate with QC physics verification
    python -m backend.cli_generate --validate --verify-qc --in-json docs/levels/level-1.json

    # Render circuit/graph images (stub for now)
    python -m backend.cli_generate --render --in-json docs/levels/level-1.json --assets-dir docs/assets
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .model import campaign_from_file
from .rounds import validate_campaign_json, validate_campaign, verify_campaign_qc
from .rendering import render_campaign_assets


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def cmd_validate(args: argparse.Namespace) -> int:
    """Run validation on a campaign JSON file."""
    json_path = Path(args.in_json)
    assets_dir = Path(args.assets_dir) if args.assets_dir else None
    
    print_header(f"Validating: {json_path}")
    
    # Basic JSON validation
    print("1. Checking JSON structure...")
    errors = validate_campaign_json(json_path, assets_dir)
    
    if errors:
        print(f"   ❌ Found {len(errors)} error(s):")
        for e in errors:
            print(f"      - {e}")
        return 1
    else:
        print("   ✓ JSON structure is valid")
    
    # Load as Campaign object
    print("\n2. Loading campaign...")
    try:
        campaign = campaign_from_file(json_path)
        print(f"   ✓ Loaded '{campaign.meta.title}' with {len(campaign.rounds)} round(s)")
    except Exception as e:
        print(f"   ❌ Failed to load campaign: {e}")
        return 1
    
    # Validate Campaign object
    print("\n3. Validating campaign object...")
    errors = validate_campaign(campaign, assets_dir)
    if errors:
        print(f"   ❌ Found {len(errors)} error(s):")
        for e in errors:
            print(f"      - {e}")
        return 1
    else:
        print("   ✓ Campaign object is valid")
    
    # QC verification (optional)
    if args.verify_qc:
        print("\n4. Running QC physics verification...")
        warnings = verify_campaign_qc(campaign)
        if warnings:
            print(f"   ⚠️  Found {len(warnings)} warning(s):")
            for w in warnings:
                print(f"      - {w}")
        else:
            print("   ✓ QC physics checks passed")
    
    print_header("Validation Complete ✓")
    
    # Print summary
    print(f"Campaign: {campaign.meta.title}")
    print(f"Subtitle: {campaign.meta.subtitle}")
    print(f"Rounds: {len(campaign.rounds)}")
    total_steps = sum(len(r.steps) for r in campaign.rounds)
    print(f"Total steps: {total_steps}")
    print(f"Timer: {'enabled' if campaign.config.timer.enabled else 'disabled'}")
    print(f"Cheat code: {'enabled' if campaign.config.cheat.enabled else 'disabled'}")
    
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    """Render circuit/graph images for a campaign."""
    json_path = Path(args.in_json)
    assets_dir = Path(args.assets_dir)
    
    print_header(f"Rendering assets for: {json_path}")
    
    try:
        campaign = campaign_from_file(json_path)
    except Exception as e:
        print(f"❌ Failed to load campaign: {e}")
        return 1
    
    print(f"Loaded '{campaign.meta.title}' with {len(campaign.rounds)} round(s)")
    print(f"Output directory: {assets_dir}")
    
    # Render assets
    rendered = render_campaign_assets(campaign, assets_dir)
    
    if rendered:
        print(f"\n✓ Rendered {len(rendered)} asset(s):")
        for path in rendered:
            print(f"   - {path}")
    else:
        print("\n⚠️  No assets were rendered (render functions are stubs)")
    
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Print info about a campaign."""
    json_path = Path(args.in_json)
    
    try:
        campaign = campaign_from_file(json_path)
    except Exception as e:
        print(f"❌ Failed to load campaign: {e}")
        return 1
    
    print_header(campaign.meta.title)
    
    if campaign.meta.subtitle:
        print(f"Subtitle: {campaign.meta.subtitle}")
    print(f"Theme: {campaign.meta.theme}")
    print(f"Schema version: {campaign.schema_version}")
    
    print(f"\nIntro slides: {len(campaign.intro_slides)}")
    for i, slide in enumerate(campaign.intro_slides):
        print(f"  {i+1}. {slide.title}")
    
    print(f"\nRounds: {len(campaign.rounds)}")
    for r in campaign.rounds:
        print(f"\n  {r.title}")
        print(f"    Difficulty: {r.difficulty}")
        print(f"    Steps: {len(r.steps)}")
        for s in r.steps:
            correct = s.answer.correct_option_id
            options = ", ".join(f"{o.id}" + ("*" if o.id == correct else "") for o in s.options)
            print(f"      - {s.id} ({s.kind}): [{options}]")
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="StabMBQC Game - Campaign validation and asset generation"
    )
    
    # Common arguments
    parser.add_argument(
        "--in-json",
        type=str,
        default="docs/levels/level-1.json",
        help="Path to the campaign JSON file"
    )
    parser.add_argument(
        "--assets-dir",
        type=str,
        default="docs/assets",
        help="Directory for assets (relative paths resolve here)"
    )
    
    # Action flags
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the campaign JSON file"
    )
    parser.add_argument(
        "--verify-qc",
        action="store_true",
        help="Run QC physics verification on steps"
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render circuit/graph images"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Print campaign info"
    )
    
    args = parser.parse_args()
    
    # Default to validate if no action specified
    if not any([args.validate, args.render, args.info]):
        args.validate = True
    
    # Run commands
    exit_code = 0
    
    if args.validate:
        exit_code = cmd_validate(args)
        if exit_code != 0:
            return exit_code
    
    if args.render:
        exit_code = cmd_render(args)
        if exit_code != 0:
            return exit_code
    
    if args.info:
        exit_code = cmd_info(args)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
