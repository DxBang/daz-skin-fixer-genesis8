import re

def parse_arguments(arguments):
	result: dict[str, list | str | bool | int | float] = {}
	result["@parameters"] = []
	skip_next = False
	for i, arg in enumerate(arguments[1:]):
		if skip_next:
			skip_next = False
			continue
		result["@parameters"].append(arg)
		if arg.startswith('-'):
			arg = arg.lstrip('-')
			parts = re.split(r'[=:]', arg, maxsplit=1)
			key = str(parts[0].lower())
			if len(parts) > 1:
				value = parts[1]
				if i + 2 < len(arguments) and not arguments[i + 2].startswith('-'):
					value += f",{arguments[i + 2]}"
					skip_next = True
				value = value.replace(',', '+').split('+')
				result[key] = value if len(value) > 1 else value[0]
			else:
				result[key] = True
	return result

def pretty_print(d, indent=0):
	for key, value in d.items():
		print('\t' * indent + f"{key}: ", end="")
		if isinstance(value, dict):
			print()
			pretty_print(value, indent + 1)
		elif isinstance(value, list):
			print()
			for item in value:
				print('\t' * (indent + 1) + f"{item}")
		else:
			print(value)
