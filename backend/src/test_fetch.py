from fec_client import fec_get

def main():
    data = fec_get("/candidates/search/", {
        "cycle": 2024,
        "per_page": 5
    })

    results = data.get("results", [])
    print(f"Fetched {len(results)} candidates")
    for c in results:
        print(c["name"], "-", c["candidate_id"])

if __name__ == "__main__":
    main()

