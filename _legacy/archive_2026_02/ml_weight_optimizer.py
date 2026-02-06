#!/usr/bin/env python3
"""
ML Weight Optimizer
Uses gradient descent to find optimal model weights for maximum accuracy
"""
import json
import numpy as np
from scipy.optimize import minimize
from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

class MLWeightOptimizer:
    def __init__(self):
        self.model = ImprovedSelfLearningModelV2()
        self.weight_names = list(self.model.get_current_weights().keys())
        
    def load_training_data(self, n=500):
        """Load historical games for training"""
        with open('data/win_probability_predictions_v2.json', 'r') as f:
            data = json.load(f)
            predictions = data.get('predictions', [])
        
        # Filter completed games with full metrics
        completed = [p for p in predictions 
                    if p.get('actual_winner') and p.get('metrics_used')]
        
        return completed[-n:]  # Last N games
    
    def calculate_log_loss(self, weights_array, games):
        """Calculate log loss for given weights"""
        # Convert array to weight dict
        weights = {name: max(0.0, min(1.0, w)) 
                  for name, w in zip(self.weight_names, weights_array)}
        
        # Normalize weights to sum to 1
        total = sum(weights.values())
        if total > 0:
            weights = {k: v/total for k, v in weights.items()}
        
        total_loss = 0.0
        count = 0
        
        for game in games:
            try:
                # Temporarily set weights
                original_weights = self.model.model_data['model_weights'].copy()
                self.model.model_data['model_weights'] = weights
                
                # Make prediction
                pred = self.model.predict_game(
                    game['away_team'],
                    game['home_team'],
                    game_date=game.get('date')
                )
                
                # Restore original weights
                self.model.model_data['model_weights'] = original_weights
                
                # Get actual outcome
                actual_winner = game['actual_winner'].lower()  # 'home' or 'away'
                
                # Get predicted probability for actual winner
                if actual_winner == 'away':
                    prob = pred['away_prob'] / 100
                elif actual_winner == 'home':
                    prob = pred['home_prob'] / 100
                else:
                    continue
                
                # Log loss (clip to avoid log(0))
                prob = max(0.001, min(0.999, prob))
                total_loss += -np.log(prob)
                count += 1
                
            except Exception as e:
                continue
        
        avg_loss = total_loss / count if count > 0 else 999.0
        return avg_loss
    
    def optimize_weights(self, games, max_iter=50):
        """Find optimal weights using gradient descent"""
        print(f"🎯 Optimizing weights on {len(games)} games...")
        print("=" * 60)
        
        # Start with current weights
        initial_weights = self.model.get_current_weights()
        x0 = np.array([initial_weights[name] for name in self.weight_names])
        
        # Normalize
        x0 = x0 / x0.sum()
        
        print(f"Initial log loss: {self.calculate_log_loss(x0, games[:100]):.4f}")
        
        # Optimize
        result = minimize(
            lambda w: self.calculate_log_loss(w, games[:100]),  # Use subset for speed
            x0,
            method='L-BFGS-B',
            bounds=[(0.0, 1.0) for _ in self.weight_names],
            options={'maxiter': max_iter, 'disp': True}
        )
        
        # Get optimized weights
        optimized_array = result.x
        optimized_array = optimized_array / optimized_array.sum()  # Normalize
        
        optimized_weights = {
            name: float(w) 
            for name, w in zip(self.weight_names, optimized_array)
        }
        
        print(f"\n✅ Optimization complete!")
        print(f"Final log loss: {result.fun:.4f}")
        
        return optimized_weights
    
    def test_optimized_weights(self, weights, test_games):
        """Test accuracy with optimized weights"""
        # Temporarily set weights
        original_weights = self.model.model_data['model_weights'].copy()
        self.model.model_data['model_weights'] = weights
        
        correct = 0
        total = 0
        
        for game in test_games:
            try:
                pred = self.model.predict_game(
                    game['away_team'],
                    game['home_team'],
                    game_date=game.get('date')
                )
                
                predicted_winner = 'away' if pred['away_prob'] > pred['home_prob'] else 'home'
                actual_winner = game['actual_winner'].lower()
                
                if predicted_winner == actual_winner:
                    correct += 1
                total += 1
                
            except:
                continue
        
        # Restore original weights
        self.model.model_data['model_weights'] = original_weights
        
        accuracy = (correct / total * 100) if total > 0 else 0
        return accuracy
    
    def save_optimized_weights(self, weights):
        """Save optimized weights to model"""
        self.model.model_data['model_weights'] = weights
        self.model.save_model_data()
        print(f"\n💾 Optimized weights saved to model!")

if __name__ == "__main__":
    optimizer = MLWeightOptimizer()
    
    print("📚 Loading training data...")
    all_games = optimizer.load_training_data(n=500)
    
    # Split into train/test
    train_games = all_games[:400]
    test_games = all_games[400:]
    
    print(f"Training set: {len(train_games)} games")
    print(f"Test set: {len(test_games)} games\n")
    
    # Test baseline
    print("📊 Baseline accuracy (current weights):")
    baseline_acc = optimizer.test_optimized_weights(
        optimizer.model.get_current_weights(),
        test_games
    )
    print(f"  {baseline_acc:.1f}%\n")
    
    # Optimize
    optimized_weights = optimizer.optimize_weights(train_games, max_iter=30)
    
    # Test optimized
    print("\n📊 Optimized accuracy:")
    optimized_acc = optimizer.test_optimized_weights(optimized_weights, test_games)
    print(f"  {optimized_acc:.1f}%")
    
    print(f"\n📈 Improvement: {optimized_acc - baseline_acc:+.1f}%")
    
    # Show top weights
    print(f"\n🔝 Top 5 Optimized Weights:")
    sorted_weights = sorted(optimized_weights.items(), key=lambda x: x[1], reverse=True)[:5]
    for name, value in sorted_weights:
        print(f"  {name}: {value:.3f}")
    
    # Ask to save
    print(f"\n💾 Save optimized weights? (This will update the model)")
    # optimizer.save_optimized_weights(optimized_weights)
