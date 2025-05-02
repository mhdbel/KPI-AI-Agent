import ahpy

def create_criteria_comparison(custom_weights=None):
    """
    Create an AHP comparison for criteria.
    Optionally override default weights using the custom_weights dict.
    """
    # Default pairwise comparisons
    comparisons = {
        ('Case Complexity', 'Staffing Levels'): 3,
        ('Case Complexity', 'Process Changes'): 5,
        ('Case Complexity', 'Technology Adjustments'): 7,
        ('Staffing Levels', 'Process Changes'): 3,
        ('Staffing Levels', 'Technology Adjustments'): 5,
        ('Process Changes', 'Technology Adjustments'): 3,
    }
    if custom_weights:
        comparisons.update(custom_weights)
    
    criteria = ahpy.Compare(name='Criteria', comparisons=comparisons, precision=3, random_index='saaty')
    return criteria

def create_alternative_comparison():
    """
    Create an AHP comparison for alternatives based on a given criterion.
    Sample comparison for options addressing 'Case Complexity'.
    """
    comparisons = {
        ('Enhanced Training', 'Process Revision'): 1/3,
        ('Enhanced Training', 'Staff Augmentation'): 1/5,
        ('Enhanced Training', 'Tech Upgrade'): 1/7,
        ('Process Revision', 'Staff Augmentation'): 3,
        ('Process Revision', 'Tech Upgrade'): 1/2,
        ('Staff Augmentation', 'Tech Upgrade'): 1/3,
    }
    alternatives = ahpy.Compare(name='Alternatives_for_Case_Complexity', comparisons=comparisons, precision=3, random_index='saaty')
    return alternatives

if __name__ == '__main__':
    criteria = create_criteria_comparison()
    print(criteria.report())
    alternatives = create_alternative_comparison()
    print(alternatives.report())
