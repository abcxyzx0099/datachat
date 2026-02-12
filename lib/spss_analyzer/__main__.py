"""
Main entry point for spss_analyzer CLI.

Provides convenient command-line interface to all survey analysis operations.
Usage: spss-analyzer <command> [options]

This script routes to the new consolidated cli.py module.
"""

import sys
import argparse

def main():
    """Main CLI entry point - routes to cli.py subcommands."""
    parser = argparse.ArgumentParser(
        description="SPSS Survey Analysis - Semantic CLI Commands",
        epilog="Examples:\n"
              "  spss-analyzer data read --sav-file survey.sav\n"
              "  spss-analyzer spec tables --metadata-file metadata.json\n"
              "  spss-analyzer analysis indicators --spec-file spec.json\n"
              "  spss-analyzer stats test --crosstabs-file cross_tables.json\n"
              "  spss-analyzer reporting both --tables-file filtered_tables.json\n"
              "  spss-analyzer all --sav-file survey.sav --output-dir output/"
    )

    # Route all commands to the consolidated cli.py
    # Strip 'spss-analyzer' prefix if present and add it
    if len(sys.argv) > 1 and sys.argv[0].endswith('spss-analyzer'):
        # User called 'spss-analyzer' directly, remove it and route to cli.py
        sys.argv = ['cli.py'] + sys.argv[1:]
    else:
        # Import cli.py as the main module
        import cli
        # Call cli.main() with the original arguments
        cli.main()

    sys.exit(0)


if __name__ == '__main__':
    main()
