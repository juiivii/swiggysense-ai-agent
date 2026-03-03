def rank_results(results, constraints):

    if not results:
        return "⚠ No results found."

    scored = []

    for r in results:
        score = 0

        # Budget scoring
        if constraints.get("budget"):
            if r["price"] <= constraints["budget"]:
                score += 3
            else:
                score -= 2

        # Rating scoring
        score += r["rating"] * 2

        # Protein scoring
        if constraints.get("high_protein"):
            protein_words = ["chicken", "egg", "paneer", "grilled", "tikka"]
            if any(word in r["dish"].lower() for word in protein_words):
                score += 3

        # Drink scoring
        if constraints.get("category") == "drink":
            drink_words = ["coffee", "shake", "juice", "soda", "lassi"]
            if any(word in r["dish"].lower() for word in drink_words):
                score += 4

        scored.append((score, r))

    scored.sort(reverse=True, key=lambda x: x[0])

    formatted = "🍽 Top Recommendations:\n\n"

    for score, item in scored[:3]:
        formatted += (
            f"🏪 {item['restaurant']}\n"
            f"🍛 {item['dish']}\n"
            f"⭐ {item['rating']}\n"
            f"💰 ₹{item['price']}\n\n"
        )

    return formatted