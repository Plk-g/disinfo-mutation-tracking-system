from backend.db.queries import get_top_claims

if __name__ == "__main__":
    top = get_top_claims(k=5)
    print("Connected. Top claims:")
    for row in top:
        print(row)
