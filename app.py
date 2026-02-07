import streamlit as st
from treys import Card, Deck, Evaluator
from itertools import combinations

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Poker Odds Assistant",
    page_icon="♠️",
    layout="centered"
)

st.title("♠️ Live Poker Odds Assistant")
st.caption("Texas Hold’em • Realtime Odds • Nuts • Threat Hands")
st.markdown("""
<style>
@keyframes slideApart {
    from {
        margin-left: -60px;
        opacity: 0.7;
        transform: translateY(4px);
    }
    to {
        margin-left: -20px;
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
""", unsafe_allow_html=True)

# st.markdown("""
# <style>
# .table {
#     background:#35654d;
#     padding:30px;
#     border-radius:18px;
#     box-shadow: inset 0 0 40px rgba(0,0,0,0.5);
# }
# .board {
#     display:flex;
#     justify-content:center;
#     gap:10px;
#     margin-bottom:30px;
# }
# .hand {
#     display:flex;
#     justify-content:center;
# }
# </style>
# """, unsafe_allow_html=True)
evaluator = Evaluator()

# =====================================================
# SESSION STATE INIT
# =====================================================
if "available_cards" not in st.session_state:
    st.session_state.available_cards = Deck().cards.copy()

if "player_cards" not in st.session_state:
    st.session_state.player_cards = []

if "board_cards" not in st.session_state:
    st.session_state.board_cards = []

if "stage" not in st.session_state:
    st.session_state.stage = "Preflop"

# =====================================================
# CONSTANTS & HELPERS
# =====================================================
SUITS = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
RANKS = ["A","K","Q","J","T","9","8","7","6","5","4","3","2"]

def pretty(card):
    r, s = Card.int_to_str(card)
    return r + SUITS[s]

# =====================================================
# DECK RENDERER (FOR DIALOGS)
# =====================================================
def render_deck_dialog(target_list, max_cards, key_prefix):
    if  len(st.session_state.player_cards) < 2 :    
        for suit in ["s", "h", "d", "c"]:
            cols = st.columns(len(RANKS))
            for i, rank in enumerate(RANKS):
                card_str = rank + suit
                card = Card.new(card_str)
                label = rank + SUITS[suit]

                if card not in st.session_state.available_cards:
                    cols[i].button("P", disabled=True, key=f"{key_prefix}_{card_str}")
                else:
                    if cols[i].button(label, key=f"{key_prefix}_{card_str}"):
                        if len(target_list) < max_cards:
                            target_list.append(card)
                            st.session_state.available_cards.remove(card)
                        st.rerun()
    elif st.session_state.stage in ["Flop", "Turn", "River"]:
        for suit in ["s", "h", "d", "c"]:
            cols = st.columns(len(RANKS))
            for i, rank in enumerate(RANKS):
                card_str = rank + suit
                card = Card.new(card_str)
                label = rank + SUITS[suit]

                if card not in st.session_state.available_cards:
                    cols[i].button("F", disabled=True, key=f"{key_prefix}_{card_str}")
                else:
                    if cols[i].button(label, key=f"{key_prefix}_{card_str}"):
                        if len(target_list) < max_cards:
                            target_list.append(card)
                            st.session_state.available_cards.remove(card)
                        st.rerun()
    else:
        for suit in ["s", "h", "d", "c"]:
            cols = st.columns(len(RANKS))
            for i, rank in enumerate(RANKS):
                card_str = rank + suit
                card = Card.new(card_str)
                label = rank + SUITS[suit]

                if card not in st.session_state.available_cards:
                    cols[i].button(" ", disabled=True, key=f"{key_prefix}_{card_str}")
                else:
                    if cols[i].button(label,disabled=True, key=f"{key_prefix}_{card_str}"):
                        if len(target_list) < max_cards:
                            target_list.append(card)
                            st.session_state.available_cards.remove(card)
                        st.rerun()


# =====================================================
# PLAYER HAND DIALOG
# =====================================================
@st.dialog("🂡 Select Your Hand")
def select_player_hand():
    st.write("Select **exactly 2 cards**")

    render_deck_dialog(
        st.session_state.player_cards,
        max_cards=2,
        key_prefix="player"
    )

    st.markdown("**Selected:** " +
        " & ".join(pretty(c) for c in st.session_state.player_cards)
    )

    col1, col2, col3 = st.columns(3)

    if col1.button("↩ Undo", disabled=len(st.session_state.player_cards) == 0):
        if st.session_state.player_cards:
            c = st.session_state.player_cards.pop()
            st.session_state.available_cards.append(c)
            st.rerun()

    if col2.button("🔄 Reset"):
        for c in st.session_state.player_cards:
            st.session_state.available_cards.append(c)
        st.session_state.player_cards = []
        st.rerun()

    if col3.button("✅ Confirm", disabled=len(st.session_state.player_cards) != 2):
        st.session_state.stage = "Flop"
        st.rerun()
    

# =====================================================
# BOARD DIALOG (FLOP / TURN / RIVER)
# =====================================================
@st.dialog("🂠 Select Community Cards")
def select_board_cards():
    stage_limits = {"Flop": 3, "Turn": 4, "River": 5}
    limit = stage_limits[st.session_state.stage]

    st.write(f"Select cards for the **{st.session_state.stage}**")

    render_deck_dialog(
        st.session_state.board_cards,
        max_cards=limit,
        key_prefix="board"
    )

    st.markdown("**Board:** " +
        " ".join(pretty(c) for c in st.session_state.board_cards)
    )

    col1, col2, col3 = st.columns(3)

    if col1.button("↩ Undo"):
        if st.session_state.board_cards:
            c = st.session_state.board_cards.pop()
            st.session_state.available_cards.append(c)
            st.rerun()

    if col2.button("🔄 Reset"):
        while len(st.session_state.board_cards) > limit - (
            1 if st.session_state.stage == "Turn" else
            2 if st.session_state.stage == "River" else 0
        ):
            c = st.session_state.board_cards.pop()
            st.session_state.available_cards.append(c)
        st.rerun()

    if col3.button("✅ Confirm", disabled=len(st.session_state.board_cards) != limit):
        st.session_state.stage = (
            "Turn" if st.session_state.stage == "Flop"
            else "River" if st.session_state.stage == "Turn"
            else "Done"
        )
        st.rerun()

# =====================================================
# MAIN UI CONTROLS
# =====================================================
if not st.session_state.player_cards or st.session_state.stage == "Preflop":
    if not st.session_state.player_cards:
        if st.button("🂡 Select Your Hand",use_container_width=True):
            select_player_hand()
    else:
        select_player_hand()
    
        

elif st.session_state.stage in ["Flop", "Turn", "River"]:
    if st.session_state.stage == "Flop":

        st.subheader("🌊 Flop")
        if 0 < len(st.session_state.board_cards) <= 3:
            select_board_cards()
        else:
            st.button(f"🂠 Select {st.session_state.stage}", use_container_width=True, on_click=select_board_cards)
    elif st.session_state.stage == "Turn":
        st.subheader("🌊 Turn")
        if len(st.session_state.board_cards) == 4:
            select_board_cards()
        else:
            st.button(f"🂠 Select {st.session_state.stage}", use_container_width=True, on_click=select_board_cards)
    
    elif st.session_state.stage == "River":
        st.subheader("🌊 River")
        if len(st.session_state.board_cards) == 5:
            select_board_cards()
        else:
            st.button(f"🂠 Select {st.session_state.stage}", use_container_width=True, on_click=select_board_cards)

    
    else:    
        if st.button(f"🂠 Select {st.session_state.stage}"):
            select_board_cards()
if st.session_state.stage == "Done":
        if st.button("🔄 Reset Game", use_container_width=True):
            # Reset everything
            st.session_state.available_cards = Deck().cards.copy()
            st.session_state.player_cards = []
            st.session_state.board_cards = []
            st.session_state.stage = "Preflop"
            st.rerun()
# =====================================================
# MONTE CARLO ODDS (AUTO)
# =====================================================
def simulate_odds(player, board, opponents=2, sims=7000):
    wins = ties = losses = 0

    for _ in range(sims):
        deck = Deck()
        for c in player + board:
            deck.cards.remove(c)

        opps = [[deck.draw(1)[0], deck.draw(1)[0]] for _ in range(opponents)]

        full_board = board[:]
        while len(full_board) < 5:
            full_board.append(deck.draw(1)[0])

        my_score = evaluator.evaluate(full_board, player)
        opp_score = min(evaluator.evaluate(full_board, o) for o in opps)

        if my_score < opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1
        else:
            losses += 1

    t = wins + ties + losses
    return wins/t, ties/t, losses/t

# =====================================================
# NUTS + THREATS
# =====================================================
def find_nuts(board, player):
    deck = Deck()
    for c in board:
        deck.cards.remove(c)

    best = 7462
    nuts = []
    for opp in combinations(deck.cards, 2):
        s = evaluator.evaluate(board, list(opp))
        if s < best:
            best = s
            nuts = [opp]
        elif s == best:
            nuts.append(opp)

    return best, nuts

def hands_that_beat(player, board, limit=9):
    deck = Deck()
    for c in player + board:
        deck.cards.remove(c)

    my_score = evaluator.evaluate(board, player)
    threats = []

    for opp in combinations(deck.cards, 2):
        s = evaluator.evaluate(board, list(opp))
        if s < my_score:
            threats.append((opp, s))

    threats.sort(key=lambda x: x[1])
    return threats[:limit]

def render_card_row(cards, key_prefix):
    cols = st.columns(len(cards))
    for i, c in enumerate(cards):
        r, s = Card.int_to_str(c)
        label = r + SUITS[s]
        cols[i].button(label, disabled=True, key=f"{key_prefix}_{i}")

def render_hand_as_cards(cards):
    card1, card2 = cards

    r1, s1 = Card.int_to_str(card1)
    r2, s2 = Card.int_to_str(card2)

    suit_symbol1 = SUITS[s1]
    suit_symbol2 = SUITS[s2]

    color1 = "red" if s1 in ["h", "d"] else "black"
    color2 = "red" if s2 in ["h", "d"] else "black"

    html = f"""
    <div class='hand'>
        <div style="display:flex; align-items:center;">
            <div style="
                width:60px;
                height:90px;
                border:1.5px solid #333;
                border-radius:8px;
                background:white;
                box-shadow:2px 2px 6px rgba(0,0,0,0.25);
                display:flex;
                flex-direction:column;
                justify-content:space-between;
                padding:4px;
                margin-left:30%;
                font-weight:bold;
                color:{color1};
            ">
                <div style="font-size:12px;">{r1}{suit_symbol1}</div>
                <div style="font-size:26px; text-align:center;">{suit_symbol1}</div>
                <div style="font-size:12px; text-align:right;">{r1}{suit_symbol1}</div>
            </div>
        <div style="display:flex; align-items:center;">
            <div style="
                width:60px;
                height:90px;
                border:1.5px solid #333;
                border-radius:8px;
                background:white;
                box-shadow:2px 2px 6px rgba(0,0,0,0.25);
                display:flex;
                flex-direction:column;
                justify-content:space-between;
                padding:4px;
                font-weight:bold;
                color:{color2};
                margin-left:-20px;
                animation: slideApart 1s ease-out;
            ">
                <div style="font-size:12px;">{r2}{suit_symbol2}</div>
                <div style="font-size:26px; text-align:center;">{suit_symbol2}</div>
                <div style="font-size:12px; text-align:right;">{r2}{suit_symbol2}</div>
            </div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def render_board_as_cards(cards,player):
    html = "<div class='table'><div style='display:flex;gap:12px;margin-left:15%;'>"
    try:

        r1, s1 = Card.int_to_str(cards[0])
        col1 = "red" if s1 in ["h", "d"] else "black"

        part1 = f"""\
        <div style='display:flex;gap:12px;'>
            <div style="width:60px;height:90px;border-radius:8px;
            background:white;border:1.5px solid #333;padding:4px;
            font-weight:bold;color:{col1};">
                <div style="font-size:12px;">{r1}{SUITS[s1]}</div>
                <div style="font-size:26px;text-align:center;">{SUITS[s1]}</div>
                <div style="font-size:12px; text-align:right;">{r1}{SUITS[s1]}</div>    
        </div>"""
    except:
        part1=""
    try:
        r2, s2 = Card.int_to_str(cards[1])
        col2 = "red" if s2 in ["h", "d"] else "black"

        part2 = f"""\
        <div style='display:flex;gap:12px;'>
            <div style="width:60px;height:90px;border-radius:8px;
            background:white;border:1.5px solid #333;padding:4px;
            font-weight:bold;color:{col2};animation: slideApart 1s ease-out;">
                <div style="font-size:12px;">{r2}{SUITS[s2]}</div>
                <div style="font-size:26px;text-align:center;">{SUITS[s2]}</div>
                <div style="font-size:12px; text-align:right;">{r2}{SUITS[s2]}</div>
        </div>"""
    except:
        part2 = ""
    try:
        r3, s3 = Card.int_to_str(cards[2])
        col3 = "red" if s3 in ["h", "d"] else "black"
        part3 = f"""\
        <div style='display:flex;gap:75px;'>
            <div style="width:60px;height:90px;border-radius:8px;
            background:white;border:1.5px solid #333;padding:4px;
            font-weight:bold;color:{col3};animation: slideApart 1s ease-out;">
                <div style="font-size:12px;">{r3}{SUITS[s3]}</div>
                <div style="font-size:26px;text-align:center;">{SUITS[s3]}</div>
                <div style="font-size:12px; text-align:right;">{r3}{SUITS[s3]}</div>
        </div>"""
    except :
        part3 = ""
    try:

        r4, s4 = Card.int_to_str(cards[3])
        col4 = "red" if s4 in ["h", "d"] else "black"
        part4 = f"""\
            <div style='display:flex;gap:75px;'>
                <div style="width:60px;height:90px;border-radius:8px;
                background:white;border:1.5px solid #333;padding:4px;
                font-weight:bold;color:{col4};animation: slideApart 1s ease-out;">
                    <div style="font-size:12px;">{r4}{SUITS[s4]}</div>
                    <div style="font-size:26px;text-align:center;">{SUITS[s4]}</div>
                    <div style="font-size:12px; text-align:right;">{r4}{SUITS[s4]}</div>
            </div>"""
    except:
        part4 = ""

    try:
        r5, s5 = Card.int_to_str(cards[4])
        col5 = "red" if s5 in ["h", "d"] else "black"
        part5 = f"""\
            <div style='display:flex;gap:12px;'>
                <div style="width:60px;height:90px;border-radius:8px;
                background:white;border:1.5px solid #333;padding:4px;
                font-weight:bold;color:{col5};animation: slideApart 1s ease-out;">
                    <div style="font-size:12px;">{r5}{SUITS[s5]}</div>
                    <div style="font-size:26px;text-align:center;">{SUITS[s5]}</div>
                    <div style="font-size:12px; text-align:right;">{r5}{SUITS[s5]}</div>
            </div>"""
    except:
        part5 = ""
    
    
    try:
        r6, s6 = Card.int_to_str(player[0])
        col6 = "red" if s6 in ["h", "d"] else "black"
        part6 = f"""\
            <div style='display:flex;gap:12px;'>
                <div style="width:60px;height:90px;border-radius:8px;
                background:white;border:1.5px solid #333;padding:4px;
                font-weight:bold;color:{col6};">
                    <div style="font-size:12px;">{r6}{SUITS[s6]}</div>
                    <div style="font-size:26px;text-align:center;">{SUITS[s6]}</div>
                    <div style="font-size:12px; text-align:right;">{r6}{SUITS[s6]}</div>
            </div>"""
    except:
        part6 = ""

    try:
        r7, s7 = Card.int_to_str(player[1])
        col7 = "red" if s7 in ["h", "d"] else "black"
        part7 = f"""\
            <div style='display:flex;gap:12px;'>
                <div style="width:60px;height:90px;border-radius:8px;
                background:white;border:1.5px solid #333;padding:4px;
                font-weight:bold;color:{col7};">
                    <div style="font-size:12px;">{r7}{SUITS[s7]}</div>
                    <div style="font-size:26px;text-align:center;">{SUITS[s7]}</div>
                    <div style="font-size:12px; text-align:right;">{r7}{SUITS[s7]}</div>
            </div>"""
    except:
        part7 = ""



    html += f"""
    <div class='table'>
{part1}
{part2}
{part3}
{part4}
{part5}
    """
    print(html)
    st.markdown(html, unsafe_allow_html=True)
def render_table_view(board, hand):
    if board:
        render_board_as_cards(board,hand)

    if len(hand) == 2:
        render_hand_as_cards(hand)


# =====================================================
# LIVE RESULTS (AUTO UPDATE)
# =====================================================
if len(st.session_state.player_cards) == 2:
    render_table_view(
        st.session_state.board_cards,
        st.session_state.player_cards
    )
    win, tie, lose = simulate_odds(
        st.session_state.player_cards,
        st.session_state.board_cards
    )

    st.divider()
    st.subheader("📊 Live Odds")

    c1, c2, c3 = st.columns(3)
    c1.metric("Win", f"{win*100:.1f}%")
    c2.metric("Tie", f"{tie*100:.1f}%")
    c3.metric("Lose", f"{lose*100:.1f}%")

    if len(st.session_state.board_cards) >= 3:
        st.divider()
        st.subheader("🔥 Nuts Analysis")

        best, nuts = find_nuts(
            st.session_state.board_cards,
            st.session_state.player_cards
        )

        my_score = evaluator.evaluate(
            st.session_state.board_cards,
            st.session_state.player_cards
        )


        if my_score == best:
            st.success("YOU HAVE THE NUTS — unbeatable hand")
        else:
            st.warning("You do NOT have the nuts (Your Score: " + str(my_score) + " | Best Possible: " + str(best) + ")")
        
            st.markdown("**Unbeatable hands:**")
            cols = st.columns(3)
            for idx, h in enumerate(nuts[:5]):
                with cols[idx % 3]:
                    render_hand_as_cards(h)

        st.divider()
        st.subheader("💀 Hands That Beat You")

        threats = hands_that_beat(
            st.session_state.player_cards,
            st.session_state.board_cards
        )

        if not threats:
            st.success("No hand can beat you")
        else:
            cols = st.columns(3)
            with st.container():
                for i, (opp, _) in enumerate(threats):
                    # st.markdown("• " + " ".join(pretty(c) for c in opp))
                    with cols[i % 3]:
                        render_hand_as_cards(opp)
                    
