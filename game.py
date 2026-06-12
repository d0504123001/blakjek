from flask import Flask, jsonify, request, session
import random

app = Flask(__name__)
# מפתח סודי נחוץ כדי להשתמש ב-session (שומר את מצב המשחק בדפדפן)
app.secret_key = 'blackjack_secret_key'

suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 10, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


def create_deck():
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck


def calculate_hand(hand):
    score = 0
    aces = 0
    for card in hand:
        score += values[card[0]]
        if card[0] == 'A':
            aces += 1
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score


# 1. נקודת קצה (Route) להתחלת משחק חדש
@app.route('/start', methods=['GET'])
def start_game():
    deck = create_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    # שמירת המצב בזיכרון של השרת עבור המשתמש
    session['deck'] = deck
    session['player_hand'] = player_hand
    session['dealer_hand'] = dealer_hand

    return jsonify({
        "message": "Game started!",
        "player_hand": player_hand,
        "player_score": calculate_hand(player_hand),
        "dealer_visible_card": dealer_hand[0]
    })


# 2. נקודת קצה ללקיחת קלף (Hit)
@app.route('/hit', methods=['GET'])
def hit():
    if 'deck' not in session:
        return jsonify({"error": "No game in progress. Go to /start"}), 400

    deck = session['deck']
    player_hand = session['player_hand']

    # משיכת קלף
    player_hand.append(deck.pop())
    player_score = calculate_hand(player_hand)

    # עדכון ה-session
    session['deck'] = deck
    session['player_hand'] = player_hand

    response = {
        "player_hand": player_hand,
        "player_score": player_score
    }

    if player_score > 21:
        response["status"] = "Bust! You lost."
        session.clear()  # איפוס המשחק

    return jsonify(response)


# 3. נקודת קצה לעצירה ותור הדילר (Stand)
@app.route('/stand', methods=['GET'])
def stand():
    if 'deck' not in session:
        return jsonify({"error": "No game in progress. Go to /start"}), 400

    deck = session['deck']
    player_hand = session['player_hand']
    dealer_hand = session['dealer_hand']

    player_score = calculate_hand(player_hand)

    # תור הדילר - מושך עד 17 ומעלה
    while calculate_hand(dealer_hand) < 17:
        dealer_hand.append(deck.pop())

    dealer_score = calculate_hand(dealer_hand)

    # קביעת תוצאה
    if dealer_score > 21:
        result = "Dealer bust! You win!"
    elif player_score > dealer_score:
        result = "You win!"
    elif player_score < dealer_score:
        result = "Dealer wins!"
    else:
        result = "Push (Tie)!"

    session.clear()  # סיום המשחק

    return jsonify({
        "result": result,
        "player_score": player_score,
        "dealer_hand": dealer_hand,
        "dealer_score": dealer_score
    })


if __name__ == '__main__':
    # הרצת השרת על פורט 5000
    app.run(debug=True, port=5000)