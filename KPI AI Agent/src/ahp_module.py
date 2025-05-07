import json
import ahpy
from typing import Dict, Any, Optional

class AHPConfigError(Exception):
    """Raised for invalid AHP configuration errors."""
    pass

class AHPHierarchy:
    """Represents an AHP hierarchy with criteria and alternatives."""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.criteria = self._build_criteria()
        self.alternatives = self._build_alternatives()
        self.root = self._build_hierarchical_structure()
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load AHP configuration from a JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise AHPConfigError(f"Configuration file not found: {path}")
        except json.JSONDecodeError as e:
            raise AHPConfigError(f"Invalid JSON format: {str(e)}")
    
    def _build_criteria(self) -> ahpy.Compare:
        """Create the criteria comparison layer."""
        criteria_config = self.config.get("criteria", {})
        comparisons = criteria_config.get("comparisons", {})
        name = criteria_config.get("name", "Criteria")
        
        criteria = ahpy.Compare(
            name=name,
            comparisons=comparisons,
            precision=3,
            random_index="saaty"
        )
        
        if criteria.consistency_ratio > 0.1:
            raise AHPConfigError(
                f"Criteria CR={criteria.consistency_ratio:.2f} (must be < 0.1)"
            )
        return criteria
    
    def _build_alternatives(self) -> Dict[str, ahpy.Compare]:
        """Create alternative comparisons for each criterion."""
        alternatives = {}
        for criterion in self.config.get("alternatives", {}):
            criterion_name = criterion["name"]
            comp = criterion["comparisons"]
            
            cmp = ahpy.Compare(
                name=f"Alternatives_for_{criterion_name}",
                comparisons=comp,
                precision=3,
                random_index="saaty"
            )
            
            if cmp.consistency_ratio > 0.1:
                raise AHPConfigError(
                    f"Alternatives for '{criterion_name}' have CR={cmp.consistency_ratio:.2f}"
                )
            alternatives[criterion_name] = cmp
        
        return alternatives
    
    def _build_hierarchical_structure(self) -> ahpy.Hierarchy:
        """Link criteria and alternatives into a hierarchy."""
        hierarchy = ahpy.Hierarchy(name="Root")
        hierarchy.add(self.criteria)
        
        for criterion in self.criteria.elements:
            criterion_node = self.criteria.elements[criterion]
            hierarchy.add_child(
                parent=self.criteria,
                child=criterion_node,
                comparison=self.alternatives[criterion]
            )
        
        return hierarchy
    
    def get_final_weights(self) -> Dict[str, float]:
        """Calculate final weights for all alternatives across criteria."""
        return self.root.get_priority_vector()
    
    def report(self) -> str:
        """Generate a comprehensive report of the AHP analysis."""
        return self.root.report()
    
def load_config(config_path: str) -> Dict[str, Any]:
    """Helper function to load AHP configuration."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise AHPConfigError(f"Failed to load config: {str(e)}")

def validate_config(config: Dict[str, Any]) -> None:
    """Validate the AHP configuration structure."""
    required_keys = ["criteria", "alternatives"]
    for key in required_keys:
        if key not in config:
            raise AHPConfigError(f"Missing required key: {key}")

    # Ensure criteria has 'name' and 'comparisons'
    criteria = config["criteria"]
    if not isinstance(criteria, dict) or "comparisons" not in criteria:
        raise AHPConfigError("Invalid criteria configuration")
    
    # Ensure alternatives have valid structure
    for alt in config["alternatives"]:
        if not all(k in alt for k in ("name", "comparisons")):
            raise AHPConfigError("Invalid alternative configuration")

def main(config_path: str):
    try:
        # Load and validate configuration
        config = load_config(config_path)
        validate_config(config)
        
        # Build AHP hierarchy
        ahp = AHPHierarchy(config_path)
        
        # Output results
        print("AHP Analysis Report:")
        print(ahp.report())
        print("\nFinal Weights:")
        for alt, weight in ahp.get_final_weights().items():
            print(f"- {alt}: {weight:.4f}")
            
    except AHPConfigError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    CONFIG_PATH = "ahp_config.json"  # Define your config path here
    main(CONFIG_PATH)
