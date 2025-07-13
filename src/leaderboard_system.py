import json
import os
from typing import List, Dict, Tuple
from datetime import datetime

class LeaderboardSystem:
    def __init__(self, filename: str = "leaderboard.json"):
        self.filename = filename
        self.scores = []
        self.max_entries = 10  # Chỉ lưu top 10
        self.load_scores()
        
    def load_scores(self):
        """Load scores from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.scores = data.get('scores', [])
            except:
                self.scores = []
        else:
            self.scores = []
            
    def save_scores(self):
        """Save scores to file"""
        try:
            data = {
                'scores': self.scores,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save leaderboard: {e}")
            
    def add_score(self, waves_survived: int, enemies_killed: int, total_score: int = None):
        """Add a new score to leaderboard"""
        if total_score is None:
            total_score = waves_survived * 100 + enemies_killed * 10
            
        score_entry = {
            'waves_survived': waves_survived,
            'enemies_killed': enemies_killed,
            'total_score': total_score,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'rank': 0
        }
        
        # Add to scores list
        self.scores.append(score_entry)
        
        # Sort by waves first, then by enemies killed
        self.scores.sort(key=lambda x: (x['waves_survived'], x['enemies_killed']), reverse=True)
        
        # Keep only top entries
        self.scores = self.scores[:self.max_entries]
        
        # Update ranks
        for i, score in enumerate(self.scores):
            score['rank'] = i + 1
            
        # Save to file
        self.save_scores()
        
        # Return rank of new score
        for i, score in enumerate(self.scores):
            if (score['waves_survived'] == waves_survived and 
                score['enemies_killed'] == enemies_killed and
                score['date'] == score_entry['date']):
                return i + 1
        return len(self.scores)
        
    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """Get top scores"""
        return self.scores[:limit]
        
    def get_player_rank(self, waves_survived: int, enemies_killed: int) -> int:
        """Get rank for a specific score"""
        for i, score in enumerate(self.scores):
            if score['waves_survived'] == waves_survived and score['enemies_killed'] == enemies_killed:
                return i + 1
        return len(self.scores) + 1
        
    def is_new_record(self, waves_survived: int, enemies_killed: int) -> bool:
        """Check if this is a new record"""
        if len(self.scores) < self.max_entries:
            return True
            
        worst_score = self.scores[-1]
        return (waves_survived > worst_score['waves_survived'] or 
                (waves_survived == worst_score['waves_survived'] and 
                 enemies_killed > worst_score['enemies_killed'])) 