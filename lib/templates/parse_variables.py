import re
import yaml

def parse_variables(
    raw_yaml: str,
    yaml_dict: dict,
    global_variables_file: str,
    gui_mode: bool = False,
    optional_vars: dict = None,
    confirm: bool = True
) -> str:
    # Handle empty input
    if not raw_yaml.strip():
        return yaml.dump({})

    # Load global variables
    try:
        with open(global_variables_file, "r", encoding="utf-8") as f:
            global_vars = yaml.safe_load(f) or {}
    except FileNotFoundError:
        global_vars = {}

    # Parse the YAML for template and local variables
    try:
        parsed_yaml = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing raw YAML: {e}")

    template_vars = parsed_yaml.get("variables", {})
    local_vars = yaml_dict.get("variables", {})
    additional_vars = optional_vars or {}

    # Ensure local_vars and additional_vars have higher precedence
    merged_vars = {**global_vars, **template_vars, **additional_vars, **local_vars}



    placeholder_pattern = re.compile(r"<(.*?)>")

    resolved_dict = {}
    resolving_stack = set()

    def resolve_value(expression: str) -> str:
        """Recursively resolve placeholders in an expression."""
        if "<" in expression and ">" not in expression:
            raise ValueError(f"Invalid placeholder syntax in: {expression}")

        placeholders = placeholder_pattern.findall(expression)
        for ph in placeholders:
            ph_value = resolve_variable(ph)
            # Replace each placeholder with its resolved value
            expression = expression.replace(f"<{ph}>", ph_value)
        return expression

    def resolve_variable(var_name: str) -> str:
        """Resolve a single variable."""
        # If we already computed this variable, return it
        if var_name in resolved_dict:

            return resolved_dict[var_name]

        # Detect circular references
        if var_name in resolving_stack:
            raise ValueError(f"Circular reference detected for variable '{var_name}'.")

        resolving_stack.add(var_name)

        # If var_name not in merged_vars, it's truly missing
        if var_name not in merged_vars:
            # Store placeholder as final value (unresolved)
            unresolved_value = f"<{var_name}>"
            resolved_dict[var_name] = unresolved_value
            resolving_stack.remove(var_name)
            return unresolved_value

        # Otherwise, we do have a value for var_name
        base_value = merged_vars[var_name]


        # Recursively resolve any placeholders in the base_value
        resolved_value = resolve_value(str(base_value))
        resolved_dict[var_name] = resolved_value
        resolving_stack.remove(var_name)
        return resolved_value

    # Resolve variables in an order that tries to handle nested placeholders first
    for key in sorted(merged_vars.keys(), key=lambda x: merged_vars[x].count('<'), reverse=True):
        resolve_variable(key)

    # Final validation of unresolved placeholders
    # We look for placeholders in the original raw_yaml...
    unresolved_placeholders = placeholder_pattern.findall(raw_yaml)


    # ...and check if they remain unresolved in resolved_dict
    for ph in unresolved_placeholders:
        # If not in resolved_dict, or if it is still "<ph>", it's unresolved
        if ph not in resolved_dict or resolved_dict[ph] == f"<{ph}>":
            raise ValueError(f"Unresolved placeholders found: {ph}")

    # Substitute placeholders in raw YAML
    def substitute_placeholder(match):
        ph = match.group(1)
        return resolved_dict.get(ph, match.group(0))  # fallback if some corner case

    resolved_yaml = placeholder_pattern.sub(substitute_placeholder, raw_yaml)

    # Confirmation prompt in non-GUI mode
    if not gui_mode and confirm:
        print("Resolved YAML:")
        print(resolved_yaml)
        user_confirm = input("Do you confirm these changes? (yes/no): ").strip().lower()
        if user_confirm != "yes":
            raise ValueError("User did not confirm the resolved YAML.")

    return resolved_yaml
