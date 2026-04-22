#!/usr/bin/env python3
import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Record named-lawyer sign-off for a redlined clause.")
    parser.add_argument("--contract", required=True, help="Contract filename (e.g. sample_negotiable.docx)")
    parser.add_argument("--clause", required=True, help="Clause family (e.g. liability_cap)")
    parser.add_argument("--lawyer", required=True, help="Full name of the approving lawyer")
    args = parser.parse_args()

    import approval
    msg = approval.record_approval(args.contract, args.clause, args.lawyer)
    print(msg)


if __name__ == "__main__":
    main()
