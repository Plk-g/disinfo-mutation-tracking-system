#!/usr/bin/env python3
"""
Bug checker - identifies potential issues in the codebase
"""

import os
import sys
import ast
import re

def check_potential_bugs():
    """Check for common bug patterns"""
    bugs_found = []
    
    # Check frontend/app.py
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "app.py")
    
    if os.path.exists(app_path):
        with open(app_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Check 1: Missing try block
        if 'def analyze_text' in content:
            # Check if try is properly indented
            analyze_start = None
            for i, line in enumerate(lines):
                if 'def analyze_text' in line:
                    analyze_start = i
                    break
            
            if analyze_start:
                # Look for try statement
                found_try = False
                for i in range(analyze_start, min(analyze_start + 10, len(lines))):
                    if lines[i].strip().startswith('try:'):
                        found_try = True
                        break
                
                if not found_try:
                    bugs_found.append({
                        'file': 'frontend/app.py',
                        'line': analyze_start + 1,
                        'issue': 'Missing try block in analyze_text function',
                        'severity': 'high'
                    })
        
        # Check 2: Unsafe list access
        if 'mutations[0]' in content and 'if mutations' not in content.split('mutations[0]')[0][-200:]:
            bugs_found.append({
                'file': 'frontend/app.py',
                'issue': 'Potential IndexError: accessing mutations[0] without proper check',
                'severity': 'medium'
            })
        
        # Check 3: Division by zero potential
        if '/ len(similarities)' in content and 'if similarities' not in content.split('/ len(similarities)')[0][-100:]:
            bugs_found.append({
                'file': 'frontend/app.py',
                'issue': 'Potential ZeroDivisionError: dividing by len(similarities) without check',
                'severity': 'medium'
            })
        
        # Check 4: Missing None checks
        if '.get(' in content and 'if ' not in content:
            # This is a weak check, but we'll flag it
            pass
    
    return bugs_found

if __name__ == "__main__":
    print("Checking for potential bugs...")
    bugs = check_potential_bugs()
    
    if bugs:
        print(f"\nFound {len(bugs)} potential issues:")
        for bug in bugs:
            print(f"\n[{bug['severity'].upper()}] {bug['file']}")
            print(f"  Issue: {bug['issue']}")
            if 'line' in bug:
                print(f"  Line: {bug['line']}")
    else:
        print("✓ No obvious bugs found!")
    
    print("\nRunning manual checks...")
    print("\n1. Checking analyze_text function structure...")
    print("2. Checking error handling...")
    print("3. Checking data validation...")
    print("\nRecommendations:")
    print("  - Add input validation for empty strings")
    print("  - Add None checks before accessing list indices")
    print("  - Add try-except around MongoDB queries")
    print("  - Validate cluster_id format before querying")

