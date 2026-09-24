from agents.job_parser.fetcher import get_job_text
from agents.job_parser.agent import parse_job


def main():
    url = input("Paste LinkedIn job URL: ").strip()

    if not url:
        print("No URL provided.")
        return

    try:
        print("\n[1/3] Fetching job page...")
        job_text = get_job_text(url)

        print("[2/3] Job description fetched successfully.")
        print("\n=== FETCHED JOB DESCRIPTION ===\n")
        print(job_text)

        print("\n[3/3] Sending job description to Job Parser...")
        job = parse_job(job_text)

        print("\n=== PARSED JOB ===\n")
        print(job.model_dump_json(indent=2))

    except Exception as error:
        print(f"\nJob Parser failed: {error}")


if __name__ == "__main__":
    main()