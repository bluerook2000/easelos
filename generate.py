#!/usr/bin/env python3
"""Easelos part generation pipeline CLI.

Usage:
    python generate.py                    # Generate all parts
    python generate.py --category bracket # Generate one category
    python generate.py --dry-run          # Count without generating
    python generate.py --output /path     # Custom output directory
"""
import argparse
import json
import os
import sys
import time

from pipeline.categories import ALL_GENERATORS, GENERATOR_MAP
from pipeline.manifest import Manifest


def main():
    parser = argparse.ArgumentParser(description="Easelos part generation pipeline")
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Generate only this category (e.g., mounting_bracket)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count parts without generating files",
    )
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)
    manifest_path = os.path.join(output_dir, "manifest.json")
    manifest = Manifest(manifest_path)

    if args.category:
        if args.category not in GENERATOR_MAP:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(GENERATOR_MAP.keys())}")
            return 1
        generators = [GENERATOR_MAP[args.category]]
    else:
        generators = ALL_GENERATORS

    total_generated = 0
    total_skipped = 0

    for gen in generators:
        print(f"\n{'='*60}")
        print(f"Category: {gen.category}")
        print(f"{'='*60}")

        start = time.time()
        all_variants = list(gen.enumerate_variants())
        total_variants = len(all_variants)

        if args.dry_run:
            new_count = sum(
                1 for v in all_variants
                if not manifest.is_generated(v.part_id, v.to_dict())
            )
            print(f"  Total variants: {total_variants}")
            print(f"  New (would generate): {new_count}")
            print(f"  Already generated: {total_variants - new_count}")
            total_generated += new_count
            total_skipped += total_variants - new_count
            continue

        generated = gen.generate_all(output_dir, manifest)
        skipped = total_variants - len(generated)
        elapsed = time.time() - start

        print(f"  Generated: {len(generated)}")
        print(f"  Skipped (already exists): {skipped}")
        print(f"  Time: {elapsed:.1f}s")

        total_generated += len(generated)
        total_skipped += skipped

        # Save manifest after each category
        manifest.save()

    print(f"\n{'='*60}")
    print(f"TOTAL: {total_generated} generated, {total_skipped} skipped")
    print(f"Manifest: {manifest_path}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
