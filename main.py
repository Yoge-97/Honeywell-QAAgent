from creator.agent import run_creator


INPUT_FILE = "input/test_input.txt"


def main():
    print("======================================")
    print("       QA CREATOR AGENT")
    print("======================================")

    result = run_creator(INPUT_FILE)

    print("\n======================================")
    print("             SUMMARY")
    print("======================================")

    print(f"Ticket       : {result['ticket_number']}")
    print(f"Branch       : {result['branch_name']}")
    print(f"Feature File : {result['feature_file']}")
    print(f"Pull Request : {result['pull_request_url']}")

    print("======================================")


if __name__ == "__main__":
    main()
