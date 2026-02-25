#!/usr/bin/env python3
"""
Initialize a skill directory structure.

Creates scripts/, references/, and assets/ directories if they don't exist.
Adds a .gitkeep file to preserve directory structure.
"""

import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Initialize skill directory structure"
    )
    parser.add_argument("skill_dir", type=Path, default=Path.cwd(),
                        help="Path to skill directory (default: current directory)")
    parser.add_argument("--force", action="store_true",
                        help="Recreate even if directories exist")

    args = parser.parse_args()
    skill_dir = args.skill_dir

    print(f"Initializing skill at: {skill_dir}")

    # Ensure we're in the correct directory
    os.chdir(skill_dir)

    # Define directories
    scripts_dir = skill_dir / "scripts"
    refs_dir = skill_dir / "references"
    assets_dir = skill_dir / "assets"

    # Create directories
    for dir_path in [scripts_dir, refs_dir, assets_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {dir_path}")

    # Add .gitkeep to preserve structure
    gitkeep = skill_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text(
            "# Skill directory structure\n"
            "# Keep this structure organized:\n"
            "# scripts/     - Executable scripts for skill operations\n"
            "# references/  - Documentation and reference materials\n"
            "# assets/       - Templates, fonts, and other resources\n"
            "\n"
            "# Rules:\n"
            "#   - Add scripts here for executable skill operations\n"
            "#   - Add documentation to references/\n"
            "#   - Add templates and assets to assets/\n"
            "#   - This structure follows skill-creator best practices\n"
        )
        print(f"  Created: {gitkeep}")

    # Create placeholder README
    readme = skill_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {skill_dir.name} Skill\n\n"
            f"\n"
            f"This skill coordinates the 7-stage survey analysis workflow.\n\n"
            f"## Usage\n\n"
            f"```bash\n"
            f"  survey-coordinator --sav-file data/survey.sav --output-dir output/\n"
            f"```\n\n"
        )
        print(f"  Created: {readme}")

    print("✅ Skill structure initialized!")


if __name__ == "__main__":
    main()
