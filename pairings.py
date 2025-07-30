#!/usr/bin/env python3
"""
Coffee Roulette Pairing Algorithm
"""

import itertools
from collections import defaultdict

def get_all_possible_pairings(people):
    """
    Generate all possible ways to pair up a list of people.
    Returns list of complete pairing solutions.
    """
    if len(people) < 2:
        return []
    
    if len(people) == 2:
        return [[[(people[0], people[1])], []]]  # [pairs, left_out]
    
    if len(people) == 3:
        # With 3 people, we have 3 possible solutions (each person left out once)
        return [
            [[(people[1], people[2])], [people[0]]],
            [[(people[0], people[2])], [people[1]]],
            [[(people[0], people[1])], [people[2]]]
        ]
    
    solutions = []
    
    # Try each person as potentially left out (if odd number)
    if len(people) % 2 == 1:
        for i, left_out_person in enumerate(people):
            remaining_people = people[:i] + people[i+1:]
            pairings = generate_pairings_for_even_group(remaining_people)
            for pairing in pairings:
                solutions.append([pairing, [left_out_person]])
    else:
        # Even number - everyone gets paired
        pairings = generate_pairings_for_even_group(people)
        for pairing in pairings:
            solutions.append([pairing, []])
    
    return solutions

def generate_pairings_for_even_group(people):
    """
    Generate all possible pairings for an even number of people.
    Returns list of pairing arrangements.
    """
    if len(people) == 0:
        return [[]]
    if len(people) == 2:
        return [[(people[0], people[1])]]
    
    # Take first person and pair with each other person
    first_person = people[0]
    remaining = people[1:]
    
    all_pairings = []
    
    for i, partner in enumerate(remaining):
        # Create this pair
        current_pair = (first_person, partner)
        
        # Get remaining people (excluding the partner)
        rest = remaining[:i] + remaining[i+1:]
        
        # Get all possible pairings for the rest
        sub_pairings = generate_pairings_for_even_group(rest)
        
        # Add current pair to each sub-pairing
        for sub_pairing in sub_pairings:
            complete_pairing = [current_pair] + sub_pairing
            all_pairings.append(complete_pairing)
    
    return all_pairings

def score_solution(pairs, left_out, data, target_week, weights=None):
    """
    Score a pairing solution based on various factors.
    
    Args:
        pairs: List of (person1, person2) tuples
        left_out: List of people left out this week
        data: Full coffee roulette data structure
        target_week: Week number we're generating for
        weights: Dict of scoring weights (optional)
    
    Returns:
        (score, breakdown) tuple
    """
    if weights is None:
        weights = {
            'first_time_meeting': 10,
            'recent_pairing_penalty': -5,  # Last 2 weeks
            'old_pairing_penalty': -1,     # 3-4 weeks ago
            'fairness_bonus': 3,           # Per times_left_out difference from average
        }
    
    score = 0
    breakdown = {
        'first_time_meetings': 0,
        'recent_pairings': 0,
        'old_pairings': 0,
        'fairness_score': 0,
        'total_pairs': len(pairs)
    }
    
    # Get historical pairings for lookups
    historical_pairs = get_historical_pairs(data)
    
    # Score each pair
    for person1, person2 in pairs:
        pair_key = tuple(sorted([person1, person2]))
        
        if pair_key not in historical_pairs:
            # First time meeting!
            score += weights['first_time_meeting']
            breakdown['first_time_meetings'] += 1
        else:
            # Check how recent the last pairing was
            last_weeks = historical_pairs[pair_key]
            most_recent = max(last_weeks)
            
            # Convert week string to comparable number (simplified)
            current_week_num = int(target_week.split('-')[1])
            recent_week_num = int(most_recent.split('-')[1])
            weeks_ago = current_week_num - recent_week_num
            
            if weeks_ago <= 2:
                score += weights['recent_pairing_penalty']
                breakdown['recent_pairings'] += 1
            elif weeks_ago <= 4:
                score += weights['old_pairing_penalty'] 
                breakdown['old_pairings'] += 1
    
    # Fairness scoring for who gets left out
    if left_out:
        people_stats = data['people']
        avg_left_out = sum(p.get('times_left_out', 0) for p in people_stats.values()) / len(people_stats)
        
        for person in left_out:
            person_left_out_count = people_stats.get(person, {}).get('times_left_out', 0)
            fairness_diff = avg_left_out - person_left_out_count
            fairness_score = fairness_diff * weights['fairness_bonus']
            score += fairness_score
            breakdown['fairness_score'] += fairness_score
    
    return score, breakdown

def get_historical_pairs(data):
    """
    Extract all historical pairings from data.
    Returns dict: {(person1, person2): [week1, week2, ...]}
    """
    pairs = defaultdict(list)
    
    for week, week_data in data.get('pairings', {}).items():
        # Handle both old and new format
        all_pairs = []
        if 'pairs' in week_data:
            all_pairs.extend(week_data['pairs'])
        if 'manual_pairs' in week_data:
            all_pairs.extend(week_data['manual_pairs'])
        if 'auto_pairs' in week_data:
            all_pairs.extend(week_data['auto_pairs'])
        
        for pair in all_pairs:
            if len(pair) == 2:
                pair_key = tuple(sorted(pair))
                pairs[pair_key].append(week)
    
    return pairs

def find_best_pairings(active_people, data, target_week, manual_pairs=None, top_n=3):
    """
    Find the best pairing solutions for active people.
    
    Args:
        active_people: List of active people names
        data: Full coffee roulette data
        target_week: Week number we're generating for
        manual_pairs: List of pre-set (person1, person2) pairs
        top_n: Number of top solutions to return
    
    Returns:
        List of (score, pairs, left_out, breakdown) tuples, sorted by score desc
    """
    if manual_pairs is None:
        manual_pairs = []
    
    # Remove manually paired people from active list
    manually_paired_people = set()
    for pair in manual_pairs:
        manually_paired_people.update(pair)
    
    available_people = [p for p in active_people if p not in manually_paired_people]
    
    print(f"Active people: {len(active_people)}")
    print(f"Manual pairs: {len(manual_pairs)}")
    print(f"People available for auto-pairing: {len(available_people)}")
    
    if len(available_people) < 2 and len(available_people) > 0:
        # Only 1 person left - they get left out
        return [(0, manual_pairs, available_people, {'note': 'Only 1 person available for auto-pairing'})]
    
    if len(available_people) == 0:
        # Everyone is manually paired
        return [(0, manual_pairs, [], {'note': 'All pairs are manual'})]
    
    # Generate all possible pairings for available people
    all_solutions = get_all_possible_pairings(available_people)
    
    print(f"Generated {len(all_solutions)} possible solutions")
    
    # Score each solution
    scored_solutions = []
    for auto_pairs, left_out in all_solutions:
        # Combine manual and auto pairs
        all_pairs = manual_pairs + auto_pairs
        score, breakdown = score_solution(all_pairs, left_out, data, target_week)
        scored_solutions.append((score, all_pairs, left_out, breakdown))
    
    # Sort by score (descending) and return top N
    scored_solutions.sort(key=lambda x: x[0], reverse=True)
    return scored_solutions[:top_n]

# Test function
def test_pairing_algorithm():
    """Test the pairing algorithm with sample data"""
    
    # Sample data
    test_data = {
        'people': {
            'Mary Jones': {'active': True, 'times_left_out': 1, 'total_weeks_participated': 5},
            'Peter Smith': {'active': True, 'times_left_out': 0, 'total_weeks_participated': 6},
            'Sarah Brown': {'active': True, 'times_left_out': 2, 'total_weeks_participated': 4},
            'John Doe': {'active': True, 'times_left_out': 0, 'total_weeks_participated': 6},
            'Lisa Wilson': {'active': True, 'times_left_out': 1, 'total_weeks_participated': 5},
        },
        'pairings': {
            '2025-29': {
                'pairs': [['Mary Jones', 'Peter Smith'], ['Sarah Brown', 'John Doe']],
                'left_out': ['Lisa Wilson']
            },
            '2025-30': {
                'pairs': [['Mary Jones', 'Sarah Brown'], ['Peter Smith', 'Lisa Wilson']],
                'left_out': ['John Doe']
            }
        }
    }
    
    active_people = ['Mary Jones', 'Peter Smith', 'Sarah Brown', 'John Doe', 'Lisa Wilson']
    target_week = '2025-31'
    
    print("=== Coffee Roulette Pairing Test ===")
    print(f"Target week: {target_week}")
    print(f"Active people: {active_people}")
    print()
    
    # Test with no manual pairs
    print("--- Solutions with no manual pairs ---")
    solutions = find_best_pairings(active_people, test_data, target_week, top_n=3)
    
    for i, (score, pairs, left_out, breakdown) in enumerate(solutions, 1):
        print(f"\nSolution {i} (Score: {score:.1f}):")
        print(f"  Pairs: {pairs}")
        print(f"  Left out: {left_out}")
        print(f"  Breakdown: {breakdown}")
    
    # Test with manual pair
    print("\n--- Solutions with manual pair: Mary + Peter ---")
    manual_pairs = [('Mary Jones', 'Peter Smith')]
    solutions = find_best_pairings(active_people, test_data, target_week, manual_pairs, top_n=3)
    
    for i, (score, pairs, left_out, breakdown) in enumerate(solutions, 1):
        print(f"\nSolution {i} (Score: {score:.1f}):")
        print(f"  Pairs: {pairs}")
        print(f"  Left out: {left_out}")
        print(f"  Breakdown: {breakdown}")

if __name__ == '__main__':
    test_pairing_algorithm()
