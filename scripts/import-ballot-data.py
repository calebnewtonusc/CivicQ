#!/usr/bin/env python3
"""
Quick Ballot Data Import Script

This script provides a simple CLI interface for importing ballot data
into CivicQ from external APIs.

Usage:
    python scripts/import-ballot-data.py --city "Los Angeles" --state "CA" --date "2024-11-05"
    python scripts/import-ballot-data.py --address "123 Main St, Los Angeles, CA 90001"
"""

import asyncio
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models.base import SessionLocal
from app.services.ballot_data_service import BallotDataService
from app.schemas.ballot_import import ImportSource


async def import_by_city(city: str, state: str, election_date: str, sources: list):
    """Import ballot data by city"""
    db = SessionLocal()

    try:
        service = BallotDataService(db)

        # Parse election date
        date_obj = datetime.strptime(election_date, "%Y-%m-%d").date()

        print(f"\n{'='*60}")
        print(f"Importing ballot data for {city}, {state}")
        print(f"Election Date: {election_date}")
        print(f"Data Sources: {', '.join(sources)}")
        print(f"{'='*60}\n")

        # Convert source strings to enum
        source_enums = [ImportSource(s) for s in sources]

        # Import ballot
        ballot = await service.import_ballot_by_city(
            city_name=city,
            state=state,
            election_date=date_obj,
            sources=source_enums,
        )

        # Display results
        print(f"\n{' SUCCESS! ':=^60}\n")
        print(f"Ballot ID: {ballot.id}")
        print(f"City: {ballot.city_name}")
        print(f"Election Date: {ballot.election_date}")
        print(f"Version: {ballot.version}")
        print(f"\nImported:")
        print(f"  - {len(ballot.contests)} contests")

        candidates_count = sum(len(c.candidates) for c in ballot.contests)
        measures_count = sum(1 for c in ballot.contests if c.type.value == "measure")

        print(f"  - {candidates_count} candidates")
        print(f"  - {measures_count} ballot measures")

        # Get import status
        status = await service.get_import_status(ballot.id)
        stats = status["statistics"]

        print(f"\nData Quality:")
        print(f"  - Contact info coverage: {stats['contact_info_percentage']:.1f}%")
        print(f"  - Candidates with contact: {stats['candidates_with_contact']}/{stats['total_candidates']}")

        print(f"\n{'='*60}")
        print(f"Next Steps:")
        print(f"  1. Review the ballot at: http://localhost:8000/api/ballots/{ballot.id}")
        print(f"  2. Add missing contact info via admin panel")
        print(f"  3. Publish the ballot to make it live")
        print(f"{'='*60}\n")

        return ballot

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


async def import_by_address(address: str, election_date: str, sources: list):
    """Import ballot data by address"""
    db = SessionLocal()

    try:
        service = BallotDataService(db)

        # Parse election date if provided
        date_obj = None
        if election_date:
            date_obj = datetime.strptime(election_date, "%Y-%m-%d").date()

        print(f"\n{'='*60}")
        print(f"Importing ballot data for address:")
        print(f"  {address}")
        if election_date:
            print(f"Election Date: {election_date}")
        else:
            print(f"Election Date: Next upcoming election")
        print(f"Data Sources: {', '.join(sources)}")
        print(f"{'='*60}\n")

        # Convert source strings to enum
        source_enums = [ImportSource(s) for s in sources]

        # Import ballot
        ballot = await service.import_ballot_by_address(
            address=address,
            election_date=date_obj,
            sources=source_enums,
        )

        # Display results (same as import_by_city)
        print(f"\n{' SUCCESS! ':=^60}\n")
        print(f"Ballot ID: {ballot.id}")
        print(f"City: {ballot.city_name}")
        print(f"Election Date: {ballot.election_date}")
        print(f"\nImported:")
        print(f"  - {len(ballot.contests)} contests")

        candidates_count = sum(len(c.candidates) for c in ballot.contests)
        measures_count = sum(1 for c in ballot.contests if c.type.value == "measure")

        print(f"  - {candidates_count} candidates")
        print(f"  - {measures_count} ballot measures")

        print(f"\n{'='*60}\n")

        return ballot

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Import ballot data from external APIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import by city
  python scripts/import-ballot-data.py --city "Los Angeles" --state "CA" --date "2024-11-05"

  # Import by address
  python scripts/import-ballot-data.py --address "123 Main St, Los Angeles, CA 90001"

  # Use specific data sources
  python scripts/import-ballot-data.py --city "Austin" --state "TX" --date "2024-11-05" --sources google_civic ballotpedia

  # Import next upcoming election
  python scripts/import-ballot-data.py --address "123 Main St, Austin, TX 78701"
        """
    )

    # City-based import
    parser.add_argument("--city", type=str, help="City name")
    parser.add_argument("--state", type=str, help="State abbreviation (e.g., CA, NY)")
    parser.add_argument("--date", type=str, help="Election date (YYYY-MM-DD)")

    # Address-based import
    parser.add_argument("--address", type=str, help="Full address")

    # Data sources
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["google_civic", "ballotpedia", "vote_america"],
        choices=["google_civic", "ballotpedia", "vote_america"],
        help="Data sources to use (default: all)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.city and args.address:
        print("ERROR: Specify either --city OR --address, not both", file=sys.stderr)
        sys.exit(1)

    if not args.city and not args.address:
        print("ERROR: Must specify either --city or --address", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if args.city and (not args.state or not args.date):
        print("ERROR: When using --city, must also specify --state and --date", file=sys.stderr)
        sys.exit(1)

    # Run import
    if args.city:
        asyncio.run(import_by_city(
            city=args.city,
            state=args.state,
            election_date=args.date,
            sources=args.sources,
        ))
    else:
        asyncio.run(import_by_address(
            address=args.address,
            election_date=args.date if args.date else None,
            sources=args.sources,
        ))


if __name__ == "__main__":
    main()
