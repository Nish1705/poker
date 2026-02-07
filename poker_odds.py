from treys import Card, Deck, Evaluator
import random

def simulate_win_probability(
    player_cards,
    community_cards,
    num_opponents,
    simulations=10000
):
    evaluator = Evaluator()
    wins = ties = losses = 0

    for _ in range(simulations):
        deck = Deck()

        # Remove known cards from deck
        known = player_cards + community_cards
        for c in known:
            deck.cards.remove(c)

        # Draw opponent hands
        opponents = []
        for _ in range(num_opponents):
            opponents.append([deck.draw(1)[0], deck.draw(1)[0]])

        # Complete community cards
        board = community_cards[:]
        while len(board) < 5:
            board.append(deck.draw(1)[0])

        # Evaluate player
        player_score = evaluator.evaluate(board, player_cards)

        opponent_scores = [
            evaluator.evaluate(board, opp) for opp in opponents
        ]

        best_opponent = min(opponent_scores)

        if player_score < best_opponent:
            wins += 1
        elif player_score == best_opponent:
            ties += 1
        else:
            losses += 1

    total = wins + ties + losses
    return {
        "win": wins / total,
        "tie": ties / total,
        "lose": losses / total
    }
