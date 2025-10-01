import json

# Load the states and actions data
with open('states_data.json', 'r') as f:
    states_data = json.load(f)

with open('actions_data.json', 'r') as f:
    actions_data = json.load(f)

# Process the data to calculate resource efficiency
agent_stats = {}

# First, process actions to get total resources earned per agent
for action in actions_data:
    agent_id = action['agent_id']
    action_type = action['action_type']
    
    if agent_id not in agent_stats:
        agent_stats[agent_id] = {
            'total_earned': 0,
            'total_steps': 0,
            'gather_actions': 0
        }
    
    if action_type == 'gather':
        amount_gathered = action.get('amount_gathered', 0)
        agent_stats[agent_id]['total_earned'] += amount_gathered
        agent_stats[agent_id]['gather_actions'] += 1
    
    agent_stats[agent_id]['total_steps'] += 1

# Then, process states to get average resource levels (reserves)
for state in states_data:
    agent_id = state['agent_id']
    resource_level = state['resource_level']
    
    if agent_id not in agent_stats:
        agent_stats[agent_id] = {
            'total_earned': 0,
            'total_steps': 0,
            'gather_actions': 0,
            'resource_levels': []
        }
    
    if 'resource_levels' not in agent_stats[agent_id]:
        agent_stats[agent_id]['resource_levels'] = []
    
    agent_stats[agent_id]['resource_levels'].append(resource_level)

# Calculate efficiency metrics
efficiency_data = []
for agent_id, stats in agent_stats.items():
    if stats['total_steps'] > 0 and len(stats.get('resource_levels', [])) > 0:
        avg_earned_per_step = stats['total_earned'] / stats['total_steps']
        avg_reserve = sum(stats['resource_levels']) / len(stats['resource_levels'])
        
        if avg_earned_per_step > 0:
            reserve_percentage = (avg_reserve / avg_earned_per_step) * 100
        else:
            reserve_percentage = 0
        
        efficiency_data.append({
            'agent_id': agent_id,
            'total_earned': stats['total_earned'],
            'total_steps': stats['total_steps'],
            'gather_actions': stats['gather_actions'],
            'avg_earned_per_step': avg_earned_per_step,
            'avg_reserve': avg_reserve,
            'reserve_percentage': reserve_percentage
        })

# Sort by reserve percentage
efficiency_data.sort(key=lambda x: x['reserve_percentage'], reverse=True)

# Print summary statistics
print('Resource Efficiency Analysis')
print('=' * 50)
print(f'Total agents analyzed: {len(efficiency_data)}')
print()

# Overall statistics
total_earned = sum(item['total_earned'] for item in efficiency_data)
total_steps = sum(item['total_steps'] for item in efficiency_data)
total_reserve = sum(item['avg_reserve'] for item in efficiency_data)

if total_steps > 0:
    overall_avg_earned_per_step = total_earned / total_steps
    overall_avg_reserve = total_reserve / len(efficiency_data)
    overall_reserve_percentage = (overall_avg_reserve / overall_avg_earned_per_step) * 100
    
    print(f'Overall Statistics:')
    print(f'  Total resources earned: {total_earned:.2f}')
    print(f'  Total steps: {total_steps}')
    print(f'  Average earned per step: {overall_avg_earned_per_step:.2f}')
    print(f'  Average reserve per agent: {overall_avg_reserve:.2f}')
    print(f'  Overall reserve percentage: {overall_reserve_percentage:.1f}%')
    print()

# Top 10 most efficient agents (highest reserve percentage)
print('Top 10 Most Efficient Agents (Highest Reserve Percentage):')
print('-' * 60)
for i, item in enumerate(efficiency_data[:10]):
    print(f'{i+1:2d}. {item["agent_id"]}: {item["reserve_percentage"]:.1f}% '
          f'(earned: {item["avg_earned_per_step"]:.2f}/step, reserve: {item["avg_reserve"]:.2f})')

print()

# Bottom 10 least efficient agents (lowest reserve percentage)
print('Bottom 10 Least Efficient Agents (Lowest Reserve Percentage):')
print('-' * 60)
for i, item in enumerate(efficiency_data[-10:]):
    print(f'{i+1:2d}. {item["agent_id"]}: {item["reserve_percentage"]:.1f}% '
          f'(earned: {item["avg_earned_per_step"]:.2f}/step, reserve: {item["avg_reserve"]:.2f})')

print()

# Distribution analysis
reserve_percentages = [item['reserve_percentage'] for item in efficiency_data]
reserve_percentages.sort()

print('Distribution of Reserve Percentages:')
print('-' * 40)
print(f'  Minimum: {min(reserve_percentages):.1f}%')
print(f'  Maximum: {max(reserve_percentages):.1f}%')
print(f'  Median: {reserve_percentages[len(reserve_percentages)//2]:.1f}%')
print(f'  Mean: {sum(reserve_percentages)/len(reserve_percentages):.1f}%')

# Percentile analysis
percentiles = [10, 25, 50, 75, 90, 95, 99]
print()
print('Percentile Analysis:')
print('-' * 30)
for p in percentiles:
    idx = int(len(reserve_percentages) * p / 100)
    if idx >= len(reserve_percentages):
        idx = len(reserve_percentages) - 1
    print(f'  {p:2d}th percentile: {reserve_percentages[idx]:.1f}%')
