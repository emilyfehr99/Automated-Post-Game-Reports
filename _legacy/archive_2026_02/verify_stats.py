from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
import logging

# Configure basic logging to avoid clutter
logging.basicConfig(level=logging.INFO)

print("Initializing model...")
model = ImprovedSelfLearningModelV2()

print("Recalculating performance...")
model.recalculate_performance_from_scratch()

perf = model.get_model_performance()
print("\n" + "="*30)
print("NEW MODEL PERFORMANCE:")
print(f"Total Games: {perf.get('total_games')}")
print(f"Accuracy: {perf.get('accuracy'):.1%}")
print(f"Recent Accuracy: {perf.get('recent_accuracy'):.1%}")
print("="*30 + "\n")
