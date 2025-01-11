from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from app.models import SuppressionScore, Stock

engine = create_engine('sqlite:///ma_suppression.db')
session = Session(engine)

# Get distribution of MA periods
ma_dist = session.query(
    SuppressionScore.ma_period,
    func.count(SuppressionScore.id)
).group_by(SuppressionScore.ma_period).all()

print('\nMA Period Distribution:')
for period, count in ma_dist:
    print(f'MA{period}: {count} scores')

# Get some example scores for different periods
print('\nExample Scores:')
for period in [10, 20, 50, 60]:
    score = session.query(SuppressionScore).join(Stock).filter(
        SuppressionScore.ma_period == period
    ).first()
    if score:
        print(f'\nMA{period} example:')
        print(f'Stock: {score.stock.symbol}')
        print(f'Score: {score.score:.4f}')
        print(f'Contacts: {score.contacts}')
        print(f'Breakthroughs: {score.breakthroughs}')
        print(f'Avg Deviation: {score.avg_deviation:.4f}')
