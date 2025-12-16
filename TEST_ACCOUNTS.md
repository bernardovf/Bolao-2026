# 🧪 Test Accounts

The database has been populated with 10 test users. You can login with any of these accounts:

## Test Users

All users have the same password: **`senha123`**

| Username | Current Ranking | Points | Exact Matches | Partial Matches |
|----------|----------------|--------|---------------|-----------------|
| Pedro Oliveira | 🥇 1st | 65 | 2 | 11 |
| Ricardo Alves | 🥈 2nd | 60 | 2 | 10 |
| Lucas Martins | 🥉 3rd | 55 | 2 | 9 |
| Fernanda Rocha | 4th | 50 | 1 | 9 |
| Beatriz Pereira | 5th | 45 | 1 | 8 |
| Ana Costa | 6th | 45 | 0 | 9 |
| Juliana Lima | 7th | 40 | 2 | 6 |
| Maria Santos | 8th | 40 | 1 | 7 |
| João Silva | 9th | 35 | 3 | 4 |
| Carlos Souza | 10th | 30 | 1 | 5 |

## Database Stats

- **Total Users**: 10
- **Total Bets**: 480 (10 users × 48 matches)
- **Matches with Results**: 20 matches
- **Matches Pending**: 28 matches

## Sample Results Added

The first 20 matches have been assigned realistic final scores, including:
- Qatar 2 x 1 Ecuador
- Senegal 1 x 1 Netherlands
- England 2 x 1 Iran
- Argentina 4 x 2 Saudi Arabia
- Poland 3 x 3 Argentina
- And 15 more...

## Betting Patterns

Users have different betting styles to make the data more realistic:
- **Conservative betters** (João, Ana, Ricardo): Predict low scores (0-2 goals)
- **Balanced betters** (Maria, Carlos, Fernanda): Predict moderate scores (0-3 goals)
- **Optimistic betters** (Pedro, Juliana, Lucas, Beatriz): Predict higher scores (1-4 goals)

## Reset Database

To reset and regenerate test data, simply run:

```bash
python3 populate_database.py
```

This will:
1. Clear all test users (keeping user ID 1)
2. Clear all test bets
3. Create 10 new users
4. Generate 480 new bets with varied patterns
5. Add 20 match results

---

**Enjoy testing your Bolão 2026! ⚽🏆**
