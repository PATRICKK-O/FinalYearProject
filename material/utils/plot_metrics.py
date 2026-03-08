import matplotlib.pyplot as plt

# Your metrics
metrics = ['Precision', 'Recall', 'F1-Score']
values = [1.00, 0.65, 0.79]

# Create a bar chart
plt.figure(figsize=(8, 5))
bars = plt.bar(metrics, values, color=['#2ecc71', '#f1c40f', '#3498db'])

# Add value labels on top of each bar
for bar, value in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f'{value:.2f}', ha='center', fontsize=11, fontweight='bold')

# Title and labels
plt.title('System Evaluation Metrics', fontsize=14, fontweight='bold')
plt.ylabel('Score', fontsize=12)
plt.ylim(0, 1.1)  # Keep chart scaled from 0 to 1
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show and save
plt.tight_layout()
plt.savefig('evaluation_metrics.png', dpi=300)
plt.show()
