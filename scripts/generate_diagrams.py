#!/usr/bin/env python3
"""
Diagram Generation Script for DataLint

Generates comprehensive UML diagrams from the datalint codebase and updates README.md
"""

import subprocess
import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Any


class CodeAnalyzer:
    """Analyzes Python codebase for diagram generation"""

    def __init__(self, source_dir: str = "datalint"):
        self.source_dir = Path(source_dir)
        self.classes: Dict[str, Dict[str, Any]] = {}
        self.modules: Dict[str, Set[str]] = {}
        self.functions: Dict[str, List[str]] = {}
        self.imports: Dict[str, Set[str]] = {}

    def analyze(self):
        """Analyze all Python files in the source directory"""
        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            self._analyze_file(py_file)

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            module_name = str(file_path.relative_to(self.source_dir)).replace('.py', '').replace('/', '.')

            self.modules[module_name] = set()
            self.functions[module_name] = []
            self.imports[module_name] = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class(node, module_name)
                elif isinstance(node, ast.FunctionDef):
                    self.functions[module_name].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[module_name].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[module_name].add(node.module)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _analyze_class(self, node: ast.ClassDef, module_name: str):
        """Analyze a class definition"""
        class_info = {
            'name': node.name,
            'module': module_name,
            'methods': [],
            'attributes': [],
            'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append({
                    'name': item.name,
                    'args': [arg.arg for arg in item.args.args]
                })
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['attributes'].append(target.id)

        self.classes[f"{module_name}.{node.name}"] = class_info
        self.modules[module_name].add(node.name)


class DiagramGenerator:
    """Generates various UML diagrams"""

    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer
        self.diagrams_dir = Path("docs/diagrams")

    def generate_all_diagrams(self):
        """Generate all diagram types"""
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)

        # Structural Diagrams
        self.generate_class_diagram()
        self.generate_component_diagram()
        self.generate_deployment_diagram()

        # Behavioral Diagrams
        self.generate_sequence_diagram()
        self.generate_activity_diagram()
        self.generate_use_case_diagram()

    def generate_class_diagram(self):
        """Generate class diagram using pyreverse"""
        try:
            cmd = [
                "pyreverse",
                "-o", "png",
                "-p", "datalint",
                "datalint"
            ]
            subprocess.run(cmd, check=True, cwd=".")
            # Move generated files to diagrams directory
            for file in Path(".").glob("*.png"):
                if "classes" in file.name or "packages" in file.name:
                    file.rename(self.diagrams_dir / file.name)
        except subprocess.CalledProcessError as e:
            print(f"Error generating class diagram: {e}")

    def generate_component_diagram(self):
        """Generate component diagram showing module relationships"""
        mermaid_content = "graph TD\n"
        mermaid_content += "    CLI[Command Line Interface]\n"
        mermaid_content += "    ENG[Core Validation Engine] \n"
        mermaid_content += "    UTI[Utility Functions]\n\n"
        mermaid_content += "    CLI --> ENG\n"
        mermaid_content += "    CLI --> UTI\n"
        mermaid_content += "    ENG --> UTI\n"

        self._generate_mermaid("component_diagram", mermaid_content)

    def generate_deployment_diagram(self):
        """Generate deployment diagram"""
        mermaid_content = "graph TD\n"
        mermaid_content += "    subgraph Local[Local Machine]\n"
        mermaid_content += "        Python[Python Environment]\n"
        mermaid_content += "        DataLint[DataLint Package]\n"
        mermaid_content += "    end\n"
        mermaid_content += "    Data[Data Files]\n"
        mermaid_content += "    Reports[Output Reports]\n\n"
        mermaid_content += "    DataLint --> Data\n"
        mermaid_content += "    DataLint --> Reports\n"
        mermaid_content += "    Python --> DataLint\n"

        self._generate_mermaid("deployment_diagram", mermaid_content)

    def generate_sequence_diagram(self):
        """Generate sequence diagram for validation workflow"""
        plantuml_content = "@startuml Sequence Diagram\n"
        plantuml_content += "autonumber\n\n"

        plantuml_content += "actor User\n"
        plantuml_content += "participant CLI\n"
        plantuml_content += "participant ValidationRunner\n"
        plantuml_content += "participant BaseValidator\n"
        plantuml_content += "participant DataFrame\n\n"

        plantuml_content += "User -> CLI: datalint validate file.csv\n"
        plantuml_content += "CLI -> ValidationRunner: run(df)\n"
        plantuml_content += "loop for each validator\n"
        plantuml_content += "  ValidationRunner -> BaseValidator: validate(df)\n"
        plantuml_content += "  BaseValidator -> DataFrame: analyze data\n"
        plantuml_content += "  DataFrame --> BaseValidator: return analysis\n"
        plantuml_content += "  BaseValidator --> ValidationRunner: ValidationResult\n"
        plantuml_content += "end\n"
        plantuml_content += "ValidationRunner --> CLI: results list\n"
        plantuml_content += "CLI --> User: formatted output\n"

        plantuml_content += "\n@enduml"

        self._generate_plantuml("sequence_diagram", plantuml_content)

    def generate_activity_diagram(self):
        """Generate activity diagram for validation pipeline"""
        plantuml_content = "@startuml Activity Diagram\n"
        plantuml_content += "start\n"

        plantuml_content += ":User runs datalint validate;\n"
        plantuml_content += ":Parse command line arguments;\n"
        plantuml_content += ":Load data file;\n"

        plantuml_content += "if (File loaded successfully?) then (yes)\n"
        plantuml_content += "  :Initialize ValidationRunner;\n"
        plantuml_content += "  :Run all validators;\n"

        plantuml_content += "  if (Validation passed?) then (yes)\n"
        plantuml_content += "    :Generate success report;\n"
        plantuml_content += "  else (no)\n"
        plantuml_content += "    :Generate failure report;\n"
        plantuml_content += "    :Show recommendations;\n"
        plantuml_content += "  endif\n"

        plantuml_content += "else (no)\n"
        plantuml_content += "  :Show error message;\n"
        plantuml_content += "endif\n"

        plantuml_content += ":Exit;\n"
        plantuml_content += "stop\n"

        plantuml_content += "\n@enduml"

        self._generate_plantuml("activity_diagram", plantuml_content)

    def generate_use_case_diagram(self):
        """Generate use case diagram"""
        plantuml_content = "@startuml Use Case Diagram\n"
        plantuml_content += "left to right direction\n\n"

        plantuml_content += "actor :Data Scientist: as DS\n"
        plantuml_content += "actor :ML Engineer: as MLE\n"
        plantuml_content += "actor :DevOps Engineer: as DevOps\n\n"

        plantuml_content += 'usecase "Validate Dataset" as UC1\n'
        plantuml_content += 'usecase "Learn from Clean Data" as UC2\n'
        plantuml_content += 'usecase "Profile Data Quality" as UC3\n'
        plantuml_content += 'usecase "Generate Reports" as UC4\n'
        plantuml_content += 'usecase "CI/CD Integration" as UC5\n\n'

        plantuml_content += "DS --> UC1\n"
        plantuml_content += "DS --> UC2\n"
        plantuml_content += "MLE --> UC3\n"
        plantuml_content += "DevOps --> UC5\n"
        plantuml_content += "UC1 --> UC4\n"
        plantuml_content += "UC2 --> UC4\n"
        plantuml_content += "UC3 --> UC4\n"

        plantuml_content += "\n@enduml"

        self._generate_plantuml("use_case_diagram", plantuml_content)

    def _generate_mermaid(self, name: str, content: str):
        """Generate Mermaid diagram file"""
        mermaid_file = self.diagrams_dir / f"{name}.mmd"

        # Write Mermaid file
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Generated Mermaid file: {mermaid_file}")

    def _generate_plantuml(self, name: str, content: str):
        """Generate PlantUML file"""
        plantuml_file = self.diagrams_dir / f"{name}.puml"

        # Write PlantUML file
        with open(plantuml_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Generated PlantUML file: {plantuml_file}")


class ReadmeUpdater:
    """Updates README.md with generated diagrams"""

    def __init__(self, diagrams_dir: Path = Path("docs/diagrams")):
        self.diagrams_dir = diagrams_dir
        self.readme_path = Path("README.md")

    def update_readme(self):
        """Update the README with diagram references"""
        if not self.readme_path.exists():
            return

        with open(self.readme_path, 'r') as f:
            content = f.read()

        # Find the architecture section
        arch_pattern = r'(### Architecture Diagrams\n\n).*?(\n---)'
        arch_match = re.search(arch_pattern, content, re.DOTALL)

        if arch_match:
            # Generate new diagrams section
            diagrams_section = self._generate_diagrams_section()

            # Replace the old section
            new_content = content.replace(arch_match.group(0), f"### Architecture Diagrams\n\n{diagrams_section}\n---")

            with open(self.readme_path, 'w') as f:
                f.write(new_content)

    def _generate_diagrams_section(self):
        """Generate the diagrams section for README"""
        diagrams = [
            ("Class Diagram", "classes_datalint.png", "Shows the class hierarchy and relationships (generated via pyreverse)"),
            ("Component Diagram", "component_diagram.mmd", "Illustrates high-level software components"),
            ("Deployment Diagram", "deployment_diagram.mmd", "Shows how the system is deployed"),
            ("Sequence Diagram", "sequence_diagram.puml", "Displays the validation workflow sequence"),
            ("Activity Diagram", "activity_diagram.puml", "Shows the validation pipeline activities"),
            ("Use Case Diagram", "use_case_diagram.puml", "Illustrates user interactions with the system")
        ]

        section = ""
        for title, filename, description in diagrams:
            diagram_path = self.diagrams_dir / filename
            print(f"Checking diagram: {diagram_path} (exists: {diagram_path.exists()})")
            if diagram_path.exists():
                section += f"#### {title}\n"
                section += f"*{description}*\n\n"
                if filename.endswith('.mmd'):
                    # GitHub renders Mermaid natively
                    section += f"```mermaid\n"
                    with open(diagram_path, 'r', encoding='utf-8') as f:
                        section += f.read()
                    section += "\n```\n\n"
                elif filename.endswith('.puml'):
                    # GitHub can render PlantUML files directly
                    section += f"```plantuml\n"
                    with open(diagram_path, 'r', encoding='utf-8') as f:
                        section += f.read()
                    section += "\n```\n\n"
                else:
                    section += f"![{title}](docs/diagrams/{filename})\n\n"

        print(f"Generated section length: {len(section)}")
        return section


def main():
    """Main entry point"""
    print("🔍 Analyzing datalint codebase...")

    analyzer = CodeAnalyzer()
    analyzer.analyze()

    print("📊 Generating diagrams...")

    generator = DiagramGenerator(analyzer)
    generator.generate_all_diagrams()

    print("📝 Updating README...")

    updater = ReadmeUpdater()
    updater.update_readme()

    print("✅ Diagram generation complete!")


if __name__ == "__main__":
    main()
