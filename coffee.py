#!/usr/bin/env python3
"""
Coffee Roulette - Weekly Team Pairing Tool
"""

import click
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DATA_FILE = Path('coffee.json')

def get_current_week():
    """Get current ISO week number"""
    today = datetime.now()
    return today.strftime('%Y-%U')

def get_next_week():
    """Get next week number from current date"""
    today = datetime.now()
    next_week = today + timedelta(days=7)
    return next_week.strftime('%Y-%U')

def load_data():
    """Load data from JSON file"""
    if not DATA_FILE.exists():
        return {
            "people": {},
            "pairings": {},
            "metadata": {
                "last_generated": "",
                "total_weeks": 0
            }
        }
    
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        click.echo("Error: Could not read coffee.json file")
        return None

def save_data(data):
    """Save data to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        click.echo(f"Error saving data: {e}")
        return False

def get_active_people(data):
    """Get list of people who are currently active"""
    return [name for name, info in data["people"].items() if info.get("active", True)]

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Coffee Roulette - Weekly Team Pairing Tool"""
    pass

@cli.command()
@click.argument('name')
def add_person(name):
    """Add a new person to the coffee roulette"""
    data = load_data()
    if data is None:
        return
    
    if name in data["people"]:
        click.echo(f"'{name}' is already in the system")
        return
    
    data["people"][name] = {
        "active": True,
        "times_left_out": 0,
        "total_weeks_participated": 0
    }
    
    if save_data(data):
        click.echo(f"Added '{name}' to coffee roulette")

@cli.command()
@click.argument('name')
def toggle(name):
    """Toggle a person's active status"""
    data = load_data()
    if data is None:
        return
    
    if name not in data["people"]:
        click.echo(f"'{name}' not found. Use 'coffee add-person' first.")
        return
    
    current_status = data["people"][name]["active"]
    data["people"][name]["active"] = not current_status
    
    new_status = "active" if not current_status else "inactive"
    
    if save_data(data):
        click.echo(f"'{name}' is now {new_status}")

@cli.command()
def list_people():
    """List all people and their status"""
    data = load_data()
    if data is None:
        return
    
    if not data["people"]:
        click.echo("No people added yet. Use 'coffee add-person' to add someone.")
        return
    
    active_people = []
    inactive_people = []
    
    for name, info in data["people"].items():
        status_info = f"{name} (left out: {info['times_left_out']}, participated: {info['total_weeks_participated']})"
        if info["active"]:
            active_people.append(status_info)
        else:
            inactive_people.append(status_info)
    
    click.echo(f"\nActive people ({len(active_people)}):")
    for person in active_people:
        click.echo(f"  ✓ {person}")
    
    if inactive_people:
        click.echo(f"\nInactive people ({len(inactive_people)}):")
        for person in inactive_people:
            click.echo(f"  ✗ {person}")
    
    click.echo("")

@cli.command()
@click.option('--week', help='Week to generate pairings for (defaults to next week)')
@click.option('--save', is_flag=True, help='Save the pairings to file')
@click.option('--overwrite', is_flag=True, help='Overwrite existing pairings for this week')
def generate_pairings(week, save, overwrite):
    """Generate pairings for the specified week"""
    data = load_data()
    if data is None:
        return
    
    # Determine week
    target_week = week or get_next_week()
    
    # Check if week already exists
    if target_week in data["pairings"] and save and not overwrite:
        click.echo(f"Error: Week {target_week} already has pairings. Use --overwrite to replace.")
        return
    
    # Get active people
    active_people = get_active_people(data)
    
    if len(active_people) < 2:
        click.echo(f"Error: Need at least 2 active people for pairings. Currently have {len(active_people)}.")
        return
    
    # TODO: Implement actual pairing logic
    # For now, just show what we would do
    click.echo(f"\nGenerating pairings for week {target_week}:")
    click.echo(f"Active people: {len(active_people)}")
    
    for name in active_people:
        click.echo(f"  - {name}")
    
    if len(active_people) % 2 == 1:
        click.echo(f"\nNote: {len(active_people)} people means 1 person will be left out this week")
    
    if save:
        # TODO: Save actual pairings
        click.echo(f"\n[Would save pairings for week {target_week}]")
    else:
        click.echo(f"\nUse --save to save these pairings for week {target_week}")

@cli.command()
@click.option('--week', required=True, help='Week to create message for')
def create_message(week):
    """Create Teams message for the specified week"""
    data = load_data()
    if data is None:
        return
    
    if week not in data["pairings"]:
        click.echo(f"Error: No pairings found for week {week}. Generate pairings first.")
        return
    
    # TODO: Create actual message from pairings
    click.echo(f"[Would create Teams message for week {week}]")

@cli.command()
@click.option('--weeks', default=5, help='Number of recent weeks to show')
def history(weeks):
    """Show pairing history"""
    data = load_data()
    if data is None:
        return
    
    if not data["pairings"]:
        click.echo("No pairing history found.")
        return
    
    # Sort weeks and show most recent
    sorted_weeks = sorted(data["pairings"].keys(), reverse=True)
    recent_weeks = sorted_weeks[:weeks]
    
    click.echo(f"\nPairing history (last {len(recent_weeks)} weeks):")
    click.echo("-" * 40)
    
    for week_num in recent_weeks:
        week_data = data["pairings"][week_num]
        click.echo(f"\nWeek {week_num}:")
        # TODO: Show actual pairings
        click.echo(f"  [Week data would be displayed here]")

if __name__ == '__main__':
    cli()
